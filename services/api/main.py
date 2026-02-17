import hashlib
import os
import secrets
import sqlite3
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path
from typing import Literal

from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field


DB_PATH = Path(os.getenv("ORBITOPS_DB_PATH", Path(__file__).with_name("orbitops.db")))


class WorkflowTemplate(BaseModel):
    id: int | None = None
    name: str
    task_type: Literal["summarize", "extract", "classify", "compare", "draft"]
    primary_model: str
    fallback_model: str
    review_required: bool
    workspace: str = "Operations Workspace"
    active: bool = True


class WorkflowCreate(BaseModel):
    name: str = Field(min_length=3)
    task_type: Literal["summarize", "extract", "classify", "compare", "draft"]
    primary_model: str = Field(min_length=3)
    fallback_model: str = Field(min_length=3)
    review_required: bool = False
    workspace: str = "Operations Workspace"


class TaskSubmission(BaseModel):
    workflow_name: str = Field(min_length=3)
    task_type: Literal["summarize", "extract", "classify", "compare", "draft"]
    latency_target: Literal["fast", "balanced", "thorough"] = "balanced"
    requires_review: bool = False
    context: str = Field(min_length=10)
    workspace: str = "Operations Workspace"
    uploaded_file_ids: list[str] = []


class RouteDecision(BaseModel):
    provider: str
    model: str
    fallback_model: str
    reason: str
    review_required: bool


class RunRecord(BaseModel):
    id: str
    workflow: str
    workspace: str
    provider: str
    model: str
    outcome: Literal["approved", "in_review", "fallback_used", "failed"]
    submitted_at: str
    context: str
    requested_by: str


class ReviewItem(BaseModel):
    id: str
    workflow: str
    summary: str
    reviewer: str
    priority: Literal["high", "medium"]
    status: Literal["open", "pending_approval", "approved", "rerun_requested"]
    requested_by: str


class ProviderHealth(BaseModel):
    provider: str
    status: Literal["online", "degraded"]
    median_latency: str
    strongest_for: str


class UploadedFile(BaseModel):
    id: str
    filename: str
    content_type: str
    workspace: str
    uploaded_at: str
    status: Literal["ready", "processing"]
    uploaded_by: str


class FileUploadRequest(BaseModel):
    filename: str = Field(min_length=3)
    content_type: str = "application/pdf"
    workspace: str = "Operations Workspace"


class ReviewDecisionRequest(BaseModel):
    decision: Literal["approve", "request_rerun"]
    actor: str = Field(min_length=2)
    note: str = Field(min_length=5)


class RegisterRequest(BaseModel):
    email: str = Field(min_length=5)
    password: str = Field(min_length=8)
    full_name: str = Field(min_length=2)
    workspace: str = "Operations Workspace"
    role: Literal["admin", "operator", "reviewer"] = "admin"


class LoginRequest(BaseModel):
    email: str = Field(min_length=5)
    password: str = Field(min_length=8)


class SessionResponse(BaseModel):
    token: str
    user: dict[str, str]


PROVIDER_MAP = {
    "claude-3-5-sonnet": "anthropic",
    "gpt-4.1": "openai",
    "gpt-4.1-mini": "openai",
    "gemini-2.0-flash": "google",
}

PROVIDER_HEALTH = [
    ProviderHealth(provider="anthropic", status="online", median_latency="2.3s", strongest_for="Document extraction"),
    ProviderHealth(provider="openai", status="online", median_latency="1.8s", strongest_for="Policy comparison"),
    ProviderHealth(provider="google", status="online", median_latency="1.4s", strongest_for="High-volume summaries"),
]

app = FastAPI(title="OrbitOps AI API", version="0.2.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@contextmanager
def db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def now_iso() -> str:
    return datetime.now(UTC).isoformat()


def display_time() -> str:
    return datetime.now(UTC).strftime("%I:%M %p")


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def initialize_database() -> None:
    with db() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                full_name TEXT NOT NULL,
                workspace TEXT NOT NULL,
                role TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS sessions (
                token TEXT PRIMARY KEY,
                user_id INTEGER NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id)
            );
            CREATE TABLE IF NOT EXISTS workflows (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                task_type TEXT NOT NULL,
                primary_model TEXT NOT NULL,
                fallback_model TEXT NOT NULL,
                review_required INTEGER NOT NULL,
                workspace TEXT NOT NULL,
                active INTEGER NOT NULL
            );
            CREATE TABLE IF NOT EXISTS files (
                id TEXT PRIMARY KEY,
                filename TEXT NOT NULL,
                content_type TEXT NOT NULL,
                workspace TEXT NOT NULL,
                uploaded_at TEXT NOT NULL,
                status TEXT NOT NULL,
                uploaded_by TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS runs (
                id TEXT PRIMARY KEY,
                workflow TEXT NOT NULL,
                workspace TEXT NOT NULL,
                provider TEXT NOT NULL,
                model TEXT NOT NULL,
                fallback_model TEXT NOT NULL,
                outcome TEXT NOT NULL,
                submitted_at TEXT NOT NULL,
                context TEXT NOT NULL,
                requested_by TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS run_files (
                run_id TEXT NOT NULL,
                file_id TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS reviews (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id TEXT NOT NULL,
                workflow TEXT NOT NULL,
                summary TEXT NOT NULL,
                reviewer TEXT NOT NULL,
                priority TEXT NOT NULL,
                status TEXT NOT NULL,
                requested_by TEXT NOT NULL,
                note TEXT DEFAULT ''
            );
            """
        )

        if conn.execute("SELECT COUNT(*) FROM users").fetchone()[0] == 0:
            conn.execute(
                """
                INSERT INTO users (email, password_hash, full_name, workspace, role)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    "admin@orbitops.local",
                    hash_password("orbitops123"),
                    "OrbitOps Admin",
                    "Operations Workspace",
                    "admin",
                ),
            )

        if conn.execute("SELECT COUNT(*) FROM workflows").fetchone()[0] == 0:
            seed_workflows = [
                ("Vendor Intake Review", "extract", "claude-3-5-sonnet", "gpt-4.1-mini", 1, "Operations Workspace", 1),
                ("Policy Delta Check", "compare", "gpt-4.1", "gemini-2.0-flash", 1, "Legal Ops", 1),
                ("Claims Summary Queue", "summarize", "gemini-2.0-flash", "claude-3-5-sonnet", 0, "Claims Ops", 1),
                ("Partner SLA Classifier", "classify", "gpt-4.1-mini", "claude-3-5-sonnet", 0, "Support Ops", 1),
            ]
            conn.executemany(
                """
                INSERT INTO workflows (name, task_type, primary_model, fallback_model, review_required, workspace, active)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                seed_workflows,
            )

        if conn.execute("SELECT COUNT(*) FROM runs").fetchone()[0] == 0:
            conn.executemany(
                """
                INSERT INTO runs (id, workflow, workspace, provider, model, fallback_model, outcome, submitted_at, context, requested_by)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        "RUN-1842",
                        "Vendor Intake Review",
                        "Operations Workspace",
                        "anthropic",
                        "claude-3-5-sonnet",
                        "gpt-4.1-mini",
                        "approved",
                        "08:31 AM",
                        "Extract vendor registration details and sanctions notes.",
                        "OrbitOps Admin",
                    ),
                    (
                        "RUN-1841",
                        "Policy Delta Check",
                        "Legal Ops",
                        "openai",
                        "gpt-4.1",
                        "gemini-2.0-flash",
                        "in_review",
                        "08:12 AM",
                        "Compare updated policy clauses and surface legal deltas.",
                        "OrbitOps Admin",
                    ),
                ],
            )
            conn.execute(
                """
                INSERT INTO reviews (run_id, workflow, summary, reviewer, priority, status, requested_by, note)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    "RUN-1841",
                    "Policy Delta Check",
                    "3 clauses changed indemnity language and need legal ops review.",
                    "Legal Ops",
                    "high",
                    "open",
                    "OrbitOps Admin",
                    "",
                ),
            )


initialize_database()


def get_user_from_token(token: str | None) -> sqlite3.Row:
    if not token:
        raise HTTPException(status_code=401, detail="Authentication required.")

    with db() as conn:
        row = conn.execute(
            """
            SELECT users.*
            FROM sessions
            JOIN users ON users.id = sessions.user_id
            WHERE sessions.token = ?
            """,
            (token,),
        ).fetchone()
    if row is None:
        raise HTTPException(status_code=401, detail="Invalid session token.")
    return row


def require_admin(token: str | None) -> sqlite3.Row:
    user = get_user_from_token(token)
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin access required.")
    return user


def next_run_id(conn: sqlite3.Connection) -> str:
    latest = conn.execute("SELECT id FROM runs ORDER BY id DESC LIMIT 1").fetchone()
    if latest is None:
        return "RUN-1841"
    return f"RUN-{int(latest['id'].split('-')[1]) + 1}"


def next_file_id(conn: sqlite3.Connection) -> str:
    latest = conn.execute("SELECT id FROM files ORDER BY id DESC LIMIT 1").fetchone()
    if latest is None:
        return "FILE-241"
    return f"FILE-{int(latest['id'].split('-')[1]) + 1}"


def workflow_by_name(conn: sqlite3.Connection, name: str) -> sqlite3.Row | None:
    return conn.execute("SELECT * FROM workflows WHERE name = ? AND active = 1", (name,)).fetchone()


def choose_route(submission: TaskSubmission, workflow: sqlite3.Row | None) -> RouteDecision:
    if workflow is None:
        model = "gpt-4.1-mini" if submission.latency_target == "fast" else "claude-3-5-sonnet"
        fallback = "gemini-2.0-flash"
        reason = "Used default policy route because the workflow template was not found."
        review_required = submission.requires_review or submission.task_type in {"compare", "extract"}
    else:
        model = workflow["primary_model"]
        fallback = workflow["fallback_model"]
        reason = f"Matched workflow policy for {workflow['task_type']} tasks."
        if submission.latency_target == "fast" and model == "claude-3-5-sonnet":
            model = "gpt-4.1-mini"
            fallback = workflow["primary_model"]
            reason = "Adjusted primary route for lower latency while preserving fallback coverage."
        review_required = submission.requires_review or bool(workflow["review_required"])

    return RouteDecision(
        provider=PROVIDER_MAP.get(model, "openai"),
        model=model,
        fallback_model=fallback,
        reason=reason,
        review_required=review_required,
    )


def serialize_workflow(row: sqlite3.Row) -> WorkflowTemplate:
    return WorkflowTemplate(
        id=row["id"],
        name=row["name"],
        task_type=row["task_type"],
        primary_model=row["primary_model"],
        fallback_model=row["fallback_model"],
        review_required=bool(row["review_required"]),
        workspace=row["workspace"],
        active=bool(row["active"]),
    )


def serialize_run(row: sqlite3.Row) -> RunRecord:
    return RunRecord(
        id=row["id"],
        workflow=row["workflow"],
        workspace=row["workspace"],
        provider=row["provider"],
        model=row["model"],
        outcome=row["outcome"],
        submitted_at=row["submitted_at"],
        context=row["context"],
        requested_by=row["requested_by"],
    )


def serialize_review(row: sqlite3.Row) -> ReviewItem:
    return ReviewItem(
        id=row["run_id"],
        workflow=row["workflow"],
        summary=row["summary"],
        reviewer=row["reviewer"],
        priority=row["priority"],
        status=row["status"],
        requested_by=row["requested_by"],
    )


def serialize_file(row: sqlite3.Row) -> UploadedFile:
    return UploadedFile(
        id=row["id"],
        filename=row["filename"],
        content_type=row["content_type"],
        workspace=row["workspace"],
        uploaded_at=row["uploaded_at"],
        status=row["status"],
        uploaded_by=row["uploaded_by"],
    )


@app.get("/health")
def healthcheck() -> dict[str, str]:
    return {"status": "ok", "service": "orbitops-api", "timestamp": now_iso()}


@app.post("/auth/register", response_model=SessionResponse)
def register(request: RegisterRequest) -> SessionResponse:
    token = secrets.token_hex(20)
    with db() as conn:
        existing = conn.execute("SELECT id FROM users WHERE email = ?", (request.email.lower(),)).fetchone()
        if existing is not None:
            raise HTTPException(status_code=409, detail="User already exists.")
        cursor = conn.execute(
            """
            INSERT INTO users (email, password_hash, full_name, workspace, role)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                request.email.lower(),
                hash_password(request.password),
                request.full_name,
                request.workspace,
                request.role,
            ),
        )
        conn.execute(
            "INSERT INTO sessions (token, user_id, created_at) VALUES (?, ?, ?)",
            (token, cursor.lastrowid, now_iso()),
        )
    return SessionResponse(
        token=token,
        user={"email": request.email.lower(), "full_name": request.full_name, "workspace": request.workspace, "role": request.role},
    )


@app.post("/auth/login", response_model=SessionResponse)
def login(request: LoginRequest) -> SessionResponse:
    with db() as conn:
        user = conn.execute(
            "SELECT * FROM users WHERE email = ? AND password_hash = ?",
            (request.email.lower(), hash_password(request.password)),
        ).fetchone()
        if user is None:
            raise HTTPException(status_code=401, detail="Invalid credentials.")
        token = secrets.token_hex(20)
        conn.execute("INSERT INTO sessions (token, user_id, created_at) VALUES (?, ?, ?)", (token, user["id"], now_iso()))
    return SessionResponse(
        token=token,
        user={
            "email": user["email"],
            "full_name": user["full_name"],
            "workspace": user["workspace"],
            "role": user["role"],
        },
    )


@app.get("/dashboard")
def dashboard() -> dict[str, object]:
    with db() as conn:
        runs = [serialize_run(row).model_dump() for row in conn.execute("SELECT * FROM runs ORDER BY id DESC LIMIT 8")]
        review_queue = [
            serialize_review(row).model_dump()
            for row in conn.execute("SELECT * FROM reviews WHERE status IN ('open', 'pending_approval') ORDER BY id DESC")
        ]
        files = [serialize_file(row).model_dump() for row in conn.execute("SELECT * FROM files ORDER BY uploaded_at DESC LIMIT 8")]
        active_workflows = conn.execute("SELECT COUNT(*) FROM workflows WHERE active = 1").fetchone()[0]
    return {
        "metrics": {
            "active_workflows": active_workflows,
            "providers_online": len(PROVIDER_HEALTH),
            "pending_reviews": len(review_queue),
            "validation_pass_rate": "98.4%",
            "uploaded_files": len(files),
        },
        "runs": runs,
        "review_queue": review_queue,
        "provider_health": [item.model_dump() for item in PROVIDER_HEALTH],
        "files": files,
    }


@app.get("/workflows")
def list_workflows() -> dict[str, list[WorkflowTemplate]]:
    with db() as conn:
        rows = conn.execute("SELECT * FROM workflows WHERE active = 1 ORDER BY name").fetchall()
    return {"items": [serialize_workflow(row) for row in rows]}


@app.post("/workflows")
def create_workflow(request: WorkflowCreate, x_auth_token: str | None = Header(default=None)) -> dict[str, WorkflowTemplate]:
    require_admin(x_auth_token)
    with db() as conn:
        cursor = conn.execute(
            """
            INSERT INTO workflows (name, task_type, primary_model, fallback_model, review_required, workspace, active)
            VALUES (?, ?, ?, ?, ?, ?, 1)
            """,
            (
                request.name,
                request.task_type,
                request.primary_model,
                request.fallback_model,
                int(request.review_required),
                request.workspace,
            ),
        )
        row = conn.execute("SELECT * FROM workflows WHERE id = ?", (cursor.lastrowid,)).fetchone()
    return {"workflow": serialize_workflow(row)}


@app.get("/runs")
def list_runs() -> dict[str, list[RunRecord]]:
    with db() as conn:
        rows = conn.execute("SELECT * FROM runs ORDER BY id DESC").fetchall()
    return {"items": [serialize_run(row) for row in rows]}


@app.get("/review")
def list_review_queue() -> dict[str, list[ReviewItem]]:
    with db() as conn:
        rows = conn.execute("SELECT * FROM reviews ORDER BY id DESC").fetchall()
    return {"items": [serialize_review(row) for row in rows]}


@app.get("/providers")
def list_providers() -> dict[str, list[ProviderHealth]]:
    return {"items": PROVIDER_HEALTH}


@app.get("/files")
def list_files() -> dict[str, list[UploadedFile]]:
    with db() as conn:
        rows = conn.execute("SELECT * FROM files ORDER BY uploaded_at DESC").fetchall()
    return {"items": [serialize_file(row) for row in rows]}


@app.post("/route")
def route_task(submission: TaskSubmission) -> dict[str, RouteDecision]:
    with db() as conn:
        workflow = workflow_by_name(conn, submission.workflow_name)
    return {"route": choose_route(submission, workflow)}


@app.post("/runs")
def create_run(submission: TaskSubmission, x_auth_token: str | None = Header(default=None)) -> dict[str, object]:
    user = get_user_from_token(x_auth_token)
    with db() as conn:
        workflow = workflow_by_name(conn, submission.workflow_name)
        route = choose_route(submission, workflow)
        run = RunRecord(
            id=next_run_id(conn),
            workflow=submission.workflow_name,
            workspace=submission.workspace,
            provider=route.provider,
            model=route.model,
            outcome="in_review" if route.review_required else "approved",
            submitted_at=display_time(),
            context=submission.context,
            requested_by=user["full_name"],
        )
        conn.execute(
            """
            INSERT INTO runs (id, workflow, workspace, provider, model, fallback_model, outcome, submitted_at, context, requested_by)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                run.id,
                run.workflow,
                run.workspace,
                run.provider,
                run.model,
                route.fallback_model,
                run.outcome,
                run.submitted_at,
                run.context,
                run.requested_by,
            ),
        )
        for file_id in submission.uploaded_file_ids:
            conn.execute("INSERT INTO run_files (run_id, file_id) VALUES (?, ?)", (run.id, file_id))
        if route.review_required:
            conn.execute(
                """
                INSERT INTO reviews (run_id, workflow, summary, reviewer, priority, status, requested_by, note)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    run.id,
                    run.workflow,
                    submission.context[:90],
                    "Operations Review",
                    "high" if submission.task_type in {"compare", "extract"} else "medium",
                    "open",
                    user["full_name"],
                    "",
                ),
            )
    return {
        "run": run,
        "route": route,
        "structured_result": {
            "status": "validated",
            "schema": "workflow_output_v1",
            "summary": f"Structured result prepared for {submission.workflow_name}.",
            "workspace": submission.workspace,
        },
    }


@app.post("/runs/simulate")
def simulate_run(submission: TaskSubmission, x_auth_token: str | None = Header(default=None)) -> dict[str, object]:
    return create_run(submission, x_auth_token)


@app.post("/files")
def create_file(request: FileUploadRequest, x_auth_token: str | None = Header(default=None)) -> dict[str, UploadedFile]:
    user = get_user_from_token(x_auth_token)
    with db() as conn:
        upload = UploadedFile(
            id=next_file_id(conn),
            filename=request.filename,
            content_type=request.content_type,
            workspace=request.workspace,
            uploaded_at=display_time(),
            status="ready",
            uploaded_by=user["full_name"],
        )
        conn.execute(
            """
            INSERT INTO files (id, filename, content_type, workspace, uploaded_at, status, uploaded_by)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                upload.id,
                upload.filename,
                upload.content_type,
                upload.workspace,
                upload.uploaded_at,
                upload.status,
                upload.uploaded_by,
            ),
        )
    return {"file": upload}


@app.post("/review/{run_id}")
def review_run(run_id: str, request: ReviewDecisionRequest, x_auth_token: str | None = Header(default=None)) -> dict[str, object]:
    get_user_from_token(x_auth_token)
    with db() as conn:
        review = conn.execute("SELECT * FROM reviews WHERE run_id = ? ORDER BY id DESC LIMIT 1", (run_id,)).fetchone()
        if review is None:
            raise HTTPException(status_code=404, detail="Review item not found.")
        run = conn.execute("SELECT * FROM runs WHERE id = ?", (run_id,)).fetchone()
        if run is None:
            raise HTTPException(status_code=404, detail="Run not found.")
        updated_outcome = "approved" if request.decision == "approve" else "failed"
        updated_status = "approved" if request.decision == "approve" else "rerun_requested"
        conn.execute("UPDATE runs SET outcome = ? WHERE id = ?", (updated_outcome, run_id))
        conn.execute(
            "UPDATE reviews SET status = ?, reviewer = ?, note = ? WHERE run_id = ?",
            (updated_status, request.actor, request.note, run_id),
        )
        updated_run = conn.execute("SELECT * FROM runs WHERE id = ?", (run_id,)).fetchone()
    return {
        "run": serialize_run(updated_run),
        "decision": {"actor": request.actor, "note": request.note, "status": request.decision},
    }

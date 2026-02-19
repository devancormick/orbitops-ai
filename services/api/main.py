import hashlib
import json
import os
import secrets
import sqlite3
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal

from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field


DB_PATH = Path(os.getenv("ORBITOPS_DB_PATH", Path(__file__).with_name("orbitops.db")))


class RegisterRequest(BaseModel):
    email: str = Field(min_length=5)
    password: str = Field(min_length=8)
    full_name: str = Field(min_length=2)
    workspace: str = "Sunline Realty"
    role: Literal["admin", "agent", "reviewer"] = "admin"


class LoginRequest(BaseModel):
    email: str = Field(min_length=5)
    password: str = Field(min_length=8)


class SessionResponse(BaseModel):
    token: str
    user: dict[str, str]


class ContractFieldDefinition(BaseModel):
    key: str
    label: str
    question: str
    required: bool = True


class ContractTemplate(BaseModel):
    id: int | None = None
    name: str
    template_key: str
    description: str
    agreement_type: Literal["listing_agreement", "purchase_sale_agreement"]
    review_required: bool
    workspace: str = "Sunline Realty"
    active: bool = True
    fields: list[ContractFieldDefinition]


class ContractTemplateCreate(BaseModel):
    name: str = Field(min_length=3)
    template_key: str = Field(min_length=3)
    description: str = Field(min_length=10)
    agreement_type: Literal["listing_agreement", "purchase_sale_agreement"]
    review_required: bool = False
    workspace: str = "Sunline Realty"
    fields: list[ContractFieldDefinition] = Field(min_length=1)


class ContractIntakeRequest(BaseModel):
    template_key: str = Field(min_length=3)
    workspace: str = "Sunline Realty"
    agent_name: str = Field(min_length=2)
    client_email: str = Field(min_length=5)
    notes: str = ""


class ContractGenerationRequest(BaseModel):
    template_key: str = Field(min_length=3)
    workspace: str = "Sunline Realty"
    agent_name: str = Field(min_length=2)
    client_email: str = Field(min_length=5)
    responses: dict[str, str]
    notes: str = ""


class DocumentDeliveryRequest(BaseModel):
    email: str = Field(min_length=5)


class GeneratedDocument(BaseModel):
    id: str
    template_name: str
    template_key: str
    agreement_type: str
    workspace: str
    status: Literal["draft", "pending_review", "ready", "emailed", "downloaded"]
    generated_at: str
    requested_by: str
    recipient_email: str
    preview_title: str
    summary: str
    field_values: dict[str, str]
    preview_markdown: str
    email_status: str
    download_status: str


class ReviewItem(BaseModel):
    id: str
    template_name: str
    summary: str
    reviewer: str
    priority: Literal["high", "medium"]
    status: Literal["open", "approved", "rerun_requested"]
    requested_by: str


app = FastAPI(title="OrbitOps AI API", version="0.3.0")
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


def field_definitions(rows: list[sqlite3.Row]) -> list[ContractFieldDefinition]:
    return [
        ContractFieldDefinition(
            key=row["field_key"],
            label=row["label"],
            question=row["question"],
            required=bool(row["required"]),
        )
        for row in rows
    ]


def base_fields(template_key: str) -> list[dict[str, Any]]:
    if template_key == "purchase-sale-agreement":
        return [
            {"key": "property_address", "label": "Property address", "question": "What property address should appear on the agreement?"},
            {"key": "buyer_name", "label": "Buyer name", "question": "Who is the buyer on the contract?"},
            {"key": "seller_name", "label": "Seller name", "question": "Who is the seller on the contract?"},
            {"key": "purchase_price", "label": "Purchase price", "question": "What is the agreed purchase price?"},
            {"key": "closing_date", "label": "Closing date", "question": "What is the closing date?"},
            {"key": "earnest_money", "label": "Earnest money", "question": "How much earnest money will be deposited?"},
        ]
    return [
        {"key": "property_address", "label": "Property address", "question": "What property address is being listed?"},
        {"key": "seller_name", "label": "Seller name", "question": "Who is the seller or owner?"},
        {"key": "listing_price", "label": "Listing price", "question": "What listing price should be used?"},
        {"key": "listing_start_date", "label": "Listing start date", "question": "When does the listing begin?"},
        {"key": "listing_end_date", "label": "Listing end date", "question": "When does the listing expire?"},
        {"key": "commission_rate", "label": "Commission rate", "question": "What commission rate should appear on the agreement?"},
    ]


def ensure_template_seed(
    conn: sqlite3.Connection,
    name: str,
    template_key: str,
    description: str,
    agreement_type: str,
    review_required: bool,
    workspace: str,
) -> None:
    existing = conn.execute("SELECT id FROM templates WHERE template_key = ?", (template_key,)).fetchone()
    if existing is not None:
        return
    cursor = conn.execute(
        """
        INSERT INTO templates (name, template_key, description, agreement_type, review_required, workspace, active)
        VALUES (?, ?, ?, ?, ?, ?, 1)
        """,
        (name, template_key, description, agreement_type, int(review_required), workspace),
    )
    for field in base_fields(template_key):
        conn.execute(
            """
            INSERT INTO template_fields (template_id, field_key, label, question, required)
            VALUES (?, ?, ?, ?, 1)
            """,
            (cursor.lastrowid, field["key"], field["label"], field["question"]),
        )


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
            CREATE TABLE IF NOT EXISTS templates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                template_key TEXT UNIQUE NOT NULL,
                description TEXT NOT NULL,
                agreement_type TEXT NOT NULL,
                review_required INTEGER NOT NULL,
                workspace TEXT NOT NULL,
                active INTEGER NOT NULL
            );
            CREATE TABLE IF NOT EXISTS template_fields (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                template_id INTEGER NOT NULL,
                field_key TEXT NOT NULL,
                label TEXT NOT NULL,
                question TEXT NOT NULL,
                required INTEGER NOT NULL,
                FOREIGN KEY (template_id) REFERENCES templates(id)
            );
            CREATE TABLE IF NOT EXISTS intake_sessions (
                id TEXT PRIMARY KEY,
                template_key TEXT NOT NULL,
                workspace TEXT NOT NULL,
                agent_name TEXT NOT NULL,
                client_email TEXT NOT NULL,
                notes TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS generated_documents (
                id TEXT PRIMARY KEY,
                template_key TEXT NOT NULL,
                template_name TEXT NOT NULL,
                agreement_type TEXT NOT NULL,
                workspace TEXT NOT NULL,
                status TEXT NOT NULL,
                generated_at TEXT NOT NULL,
                requested_by TEXT NOT NULL,
                recipient_email TEXT NOT NULL,
                preview_title TEXT NOT NULL,
                summary TEXT NOT NULL,
                preview_markdown TEXT NOT NULL,
                field_values_json TEXT NOT NULL,
                email_status TEXT NOT NULL,
                download_status TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS reviews (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                document_id TEXT NOT NULL,
                template_name TEXT NOT NULL,
                summary TEXT NOT NULL,
                reviewer TEXT NOT NULL,
                priority TEXT NOT NULL,
                status TEXT NOT NULL,
                requested_by TEXT NOT NULL
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
                    "D. Cormick",
                    "Sunline Realty",
                    "admin",
                ),
            )

        ensure_template_seed(
            conn,
            "Listing Agreement",
            "listing-agreement",
            "Guided listing contract flow for property owners, commission terms, and listing dates.",
            "listing_agreement",
            True,
            "Sunline Realty",
        )
        ensure_template_seed(
            conn,
            "Purchase & Sale Agreement",
            "purchase-sale-agreement",
            "Guided purchase contract flow for buyers, sellers, price, earnest money, and closing.",
            "purchase_sale_agreement",
            True,
            "Sunline Realty",
        )

        if conn.execute("SELECT COUNT(*) FROM generated_documents").fetchone()[0] == 0:
            seed_values = {
                "property_address": "414 Maple Ridge Drive, Nashville, TN",
                "seller_name": "Claire Hudson",
                "listing_price": "$685,000",
                "listing_start_date": "2026-02-24",
                "listing_end_date": "2026-08-24",
                "commission_rate": "5.5%",
            }
            conn.execute(
                """
                INSERT INTO generated_documents
                (id, template_key, template_name, agreement_type, workspace, status, generated_at, requested_by, recipient_email,
                 preview_title, summary, preview_markdown, field_values_json, email_status, download_status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    "DOC-4021",
                    "listing-agreement",
                    "Listing Agreement",
                    "listing_agreement",
                    "Sunline Realty",
                    "pending_review",
                    "09:12 AM",
                    "D. Cormick",
                    "agent@sunlinerealty.com",
                    "Listing Agreement for 414 Maple Ridge Drive",
                    "Listing packet generated and waiting for broker review before delivery.",
                    render_preview("Listing Agreement", seed_values),
                    json.dumps(seed_values),
                    "not_sent",
                    "ready",
                ),
            )
            conn.execute(
                """
                INSERT INTO reviews (document_id, template_name, summary, reviewer, priority, status, requested_by)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    "DOC-4021",
                    "Listing Agreement",
                    "Commission and listing dates should be confirmed before release.",
                    "Broker Review",
                    "high",
                    "open",
                    "D. Cormick",
                ),
            )


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


def next_sequence_id(conn: sqlite3.Connection, table: str, prefix: str) -> str:
    row = conn.execute(f"SELECT id FROM {table} ORDER BY id DESC LIMIT 1").fetchone()
    if row is None:
        return f"{prefix}-1001"
    return f"{prefix}-{int(row['id'].split('-')[1]) + 1}"


def template_with_fields(conn: sqlite3.Connection, template_key: str) -> sqlite3.Row | None:
    return conn.execute("SELECT * FROM templates WHERE template_key = ? AND active = 1", (template_key,)).fetchone()


def serialize_template(conn: sqlite3.Connection, row: sqlite3.Row) -> ContractTemplate:
    field_rows = conn.execute(
        "SELECT * FROM template_fields WHERE template_id = ? ORDER BY id",
        (row["id"],),
    ).fetchall()
    return ContractTemplate(
        id=row["id"],
        name=row["name"],
        template_key=row["template_key"],
        description=row["description"],
        agreement_type=row["agreement_type"],
        review_required=bool(row["review_required"]),
        workspace=row["workspace"],
        active=bool(row["active"]),
        fields=field_definitions(field_rows),
    )


def serialize_document(row: sqlite3.Row) -> GeneratedDocument:
    return GeneratedDocument(
        id=row["id"],
        template_name=row["template_name"],
        template_key=row["template_key"],
        agreement_type=row["agreement_type"],
        workspace=row["workspace"],
        status=row["status"],
        generated_at=row["generated_at"],
        requested_by=row["requested_by"],
        recipient_email=row["recipient_email"],
        preview_title=row["preview_title"],
        summary=row["summary"],
        field_values=json.loads(row["field_values_json"]),
        preview_markdown=row["preview_markdown"],
        email_status=row["email_status"],
        download_status=row["download_status"],
    )


def serialize_review(row: sqlite3.Row) -> ReviewItem:
    return ReviewItem(
        id=row["document_id"],
        template_name=row["template_name"],
        summary=row["summary"],
        reviewer=row["reviewer"],
        priority=row["priority"],
        status=row["status"],
        requested_by=row["requested_by"],
    )


def render_preview(template_name: str, values: dict[str, str]) -> str:
    lines = [f"# {template_name}", ""]
    for key, value in values.items():
        label = key.replace("_", " ").title()
        lines.append(f"- {label}: {value}")
    lines.append("")
    lines.append("Prepared through the OrbitOps AI contract generator demo.")
    return "\n".join(lines)


def summarize_document(template_name: str, values: dict[str, str]) -> str:
    property_address = values.get("property_address", "the property")
    principal = values.get("seller_name") or values.get("buyer_name") or "the client"
    return f"{template_name} prepared for {principal} covering {property_address}."


initialize_database()


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
        user={
            "email": request.email.lower(),
            "full_name": request.full_name,
            "workspace": request.workspace,
            "role": request.role,
        },
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
        templates = conn.execute("SELECT COUNT(*) FROM templates WHERE active = 1").fetchone()[0]
        documents = [serialize_document(row).model_dump() for row in conn.execute("SELECT * FROM generated_documents ORDER BY id DESC LIMIT 8")]
        review_queue = [
            serialize_review(row).model_dump()
            for row in conn.execute("SELECT * FROM reviews WHERE status = 'open' ORDER BY id DESC LIMIT 8")
        ]
    return {
        "metrics": {
            "active_templates": templates,
            "generated_documents": len(documents),
            "pending_reviews": len(review_queue),
            "delivery_readiness": "Demo ready",
        },
        "documents": documents,
        "review_queue": review_queue,
    }


@app.get("/templates")
def list_templates() -> dict[str, list[ContractTemplate]]:
    with db() as conn:
        rows = conn.execute("SELECT * FROM templates WHERE active = 1 ORDER BY name").fetchall()
        items = [serialize_template(conn, row) for row in rows]
    return {"items": items}


@app.post("/templates")
def create_template(
    request: ContractTemplateCreate,
    x_auth_token: str | None = Header(default=None),
) -> dict[str, ContractTemplate]:
    require_admin(x_auth_token)
    with db() as conn:
        cursor = conn.execute(
            """
            INSERT INTO templates (name, template_key, description, agreement_type, review_required, workspace, active)
            VALUES (?, ?, ?, ?, ?, ?, 1)
            """,
            (
                request.name,
                request.template_key,
                request.description,
                request.agreement_type,
                int(request.review_required),
                request.workspace,
            ),
        )
        for field in request.fields:
            conn.execute(
                """
                INSERT INTO template_fields (template_id, field_key, label, question, required)
                VALUES (?, ?, ?, ?, ?)
                """,
                (cursor.lastrowid, field.key, field.label, field.question, int(field.required)),
            )
        row = conn.execute("SELECT * FROM templates WHERE id = ?", (cursor.lastrowid,)).fetchone()
        template = serialize_template(conn, row)
    return {"template": template}


@app.post("/intake/start")
def start_intake(
    request: ContractIntakeRequest,
    x_auth_token: str | None = Header(default=None),
) -> dict[str, object]:
    get_user_from_token(x_auth_token)
    with db() as conn:
        template = template_with_fields(conn, request.template_key)
        if template is None:
            raise HTTPException(status_code=404, detail="Template not found.")
        session_id = next_sequence_id(conn, "intake_sessions", "INTAKE")
        conn.execute(
            """
            INSERT INTO intake_sessions (id, template_key, workspace, agent_name, client_email, notes, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                session_id,
                request.template_key,
                request.workspace,
                request.agent_name,
                request.client_email,
                request.notes,
                now_iso(),
            ),
        )
        serialized_template = serialize_template(conn, template)
    return {
        "session": {
            "id": session_id,
            "template_key": request.template_key,
            "agent_name": request.agent_name,
            "client_email": request.client_email,
            "workspace": request.workspace,
            "assistant_prompt": f"I will help prepare the {serialized_template.name} by collecting the required deal fields one at a time.",
            "questions": [field.model_dump() for field in serialized_template.fields],
        }
    }


@app.post("/documents/generate")
def generate_document(
    request: ContractGenerationRequest,
    x_auth_token: str | None = Header(default=None),
) -> dict[str, object]:
    user = get_user_from_token(x_auth_token)
    with db() as conn:
        template = template_with_fields(conn, request.template_key)
        if template is None:
            raise HTTPException(status_code=404, detail="Template not found.")
        serialized_template = serialize_template(conn, template)
        required_keys = {field.key for field in serialized_template.fields if field.required}
        missing = sorted(key for key in required_keys if not str(request.responses.get(key, "")).strip())
        if missing:
            raise HTTPException(status_code=422, detail=f"Missing required fields: {', '.join(missing)}")

        document_id = next_sequence_id(conn, "generated_documents", "DOC")
        status = "pending_review" if serialized_template.review_required else "ready"
        summary = summarize_document(serialized_template.name, request.responses)
        preview_title = f"{serialized_template.name} for {request.responses.get('property_address', 'the property')}"
        preview_markdown = render_preview(serialized_template.name, request.responses)
        document = GeneratedDocument(
            id=document_id,
            template_name=serialized_template.name,
            template_key=serialized_template.template_key,
            agreement_type=serialized_template.agreement_type,
            workspace=request.workspace,
            status=status,
            generated_at=display_time(),
            requested_by=user["full_name"],
            recipient_email=request.client_email,
            preview_title=preview_title,
            summary=summary,
            field_values=request.responses,
            preview_markdown=preview_markdown,
            email_status="not_sent",
            download_status="ready",
        )
        conn.execute(
            """
            INSERT INTO generated_documents
            (id, template_key, template_name, agreement_type, workspace, status, generated_at, requested_by, recipient_email,
             preview_title, summary, preview_markdown, field_values_json, email_status, download_status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                document.id,
                document.template_key,
                document.template_name,
                document.agreement_type,
                document.workspace,
                document.status,
                document.generated_at,
                document.requested_by,
                document.recipient_email,
                document.preview_title,
                document.summary,
                document.preview_markdown,
                json.dumps(document.field_values),
                document.email_status,
                document.download_status,
            ),
        )
        if serialized_template.review_required:
            conn.execute(
                """
                INSERT INTO reviews (document_id, template_name, summary, reviewer, priority, status, requested_by)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    document.id,
                    document.template_name,
                    f"Review generated {document.template_name.lower()} before agent delivery.",
                    "Broker Review",
                    "high",
                    "open",
                    user["full_name"],
                ),
            )
    return {
        "document": document,
        "delivery": {
            "download_ready": True,
            "email_ready": True,
            "mode": "demo",
        },
    }


@app.get("/documents")
def list_documents() -> dict[str, list[GeneratedDocument]]:
    with db() as conn:
        rows = conn.execute("SELECT * FROM generated_documents ORDER BY id DESC").fetchall()
    return {"items": [serialize_document(row) for row in rows]}


@app.post("/documents/{document_id}/email")
def email_document(
    document_id: str,
    request: DocumentDeliveryRequest,
    x_auth_token: str | None = Header(default=None),
) -> dict[str, object]:
    get_user_from_token(x_auth_token)
    with db() as conn:
        row = conn.execute("SELECT * FROM generated_documents WHERE id = ?", (document_id,)).fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="Document not found.")
        conn.execute(
            "UPDATE generated_documents SET email_status = ?, recipient_email = ?, status = ? WHERE id = ?",
            ("sent_demo", request.email, "emailed", document_id),
        )
        updated = conn.execute("SELECT * FROM generated_documents WHERE id = ?", (document_id,)).fetchone()
    return {
        "document": serialize_document(updated),
        "delivery": {"channel": "email", "status": "sent_demo", "email": request.email},
    }


@app.post("/documents/{document_id}/download")
def download_document(document_id: str, x_auth_token: str | None = Header(default=None)) -> dict[str, object]:
    get_user_from_token(x_auth_token)
    with db() as conn:
        row = conn.execute("SELECT * FROM generated_documents WHERE id = ?", (document_id,)).fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="Document not found.")
        conn.execute(
            "UPDATE generated_documents SET download_status = ?, status = ? WHERE id = ?",
            ("downloaded_demo", "downloaded", document_id),
        )
        updated = conn.execute("SELECT * FROM generated_documents WHERE id = ?", (document_id,)).fetchone()
    return {
        "document": serialize_document(updated),
        "delivery": {"channel": "download", "status": "downloaded_demo", "filename": f"{document_id}.pdf"},
    }


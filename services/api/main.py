from datetime import UTC, datetime
from typing import Literal

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field


class WorkflowTemplate(BaseModel):
    name: str
    task_type: Literal["summarize", "extract", "classify", "compare", "draft"]
    primary_model: str
    fallback_model: str
    review_required: bool


class TaskSubmission(BaseModel):
    workflow_name: str = Field(min_length=3)
    task_type: Literal["summarize", "extract", "classify", "compare", "draft"]
    latency_target: Literal["fast", "balanced", "thorough"] = "balanced"
    requires_review: bool = False
    context: str = Field(min_length=10)
    workspace: str = "Operations Workspace"


class RouteDecision(BaseModel):
    provider: str
    model: str
    fallback_model: str
    reason: str
    review_required: bool


class RunRecord(BaseModel):
    id: str
    workflow: str
    provider: str
    model: str
    outcome: Literal["approved", "in_review", "fallback_used", "failed"]
    submitted_at: str


class ReviewItem(BaseModel):
    id: str
    workflow: str
    summary: str
    reviewer: str
    priority: Literal["high", "medium"]
    status: Literal["open", "pending_approval"]


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


class FileUploadRequest(BaseModel):
    filename: str = Field(min_length=3)
    content_type: str = "application/pdf"
    workspace: str = "Operations Workspace"


class ReviewDecisionRequest(BaseModel):
    decision: Literal["approve", "request_rerun"]
    actor: str = Field(min_length=2)
    note: str = Field(min_length=5)


WORKFLOWS = [
    WorkflowTemplate(
        name="Vendor Intake Review",
        task_type="extract",
        primary_model="claude-3-5-sonnet",
        fallback_model="gpt-4.1-mini",
        review_required=True,
    ),
    WorkflowTemplate(
        name="Policy Delta Check",
        task_type="compare",
        primary_model="gpt-4.1",
        fallback_model="gemini-2.0-flash",
        review_required=True,
    ),
    WorkflowTemplate(
        name="Claims Summary Queue",
        task_type="summarize",
        primary_model="gemini-2.0-flash",
        fallback_model="claude-3-5-sonnet",
        review_required=False,
    ),
]

PROVIDER_MAP = {
    "claude-3-5-sonnet": "anthropic",
    "gpt-4.1": "openai",
    "gpt-4.1-mini": "openai",
    "gemini-2.0-flash": "google",
}

RUNS = [
    RunRecord(
        id="RUN-1842",
        workflow="Vendor Intake Review",
        provider="anthropic",
        model="claude-3-5-sonnet",
        outcome="approved",
        submitted_at="08:31 AM",
    ),
    RunRecord(
        id="RUN-1841",
        workflow="Policy Delta Check",
        provider="openai",
        model="gpt-4.1",
        outcome="in_review",
        submitted_at="08:12 AM",
    ),
    RunRecord(
        id="RUN-1839",
        workflow="Claims Summary Queue",
        provider="google",
        model="gemini-2.0-flash",
        outcome="fallback_used",
        submitted_at="07:44 AM",
    ),
]

REVIEW_QUEUE = [
    ReviewItem(
        id="RUN-1841",
        workflow="Policy Delta Check",
        summary="3 clauses changed indemnity language and need legal ops review.",
        reviewer="Legal Ops",
        priority="high",
        status="open",
    ),
    ReviewItem(
        id="RUN-1838",
        workflow="Vendor Intake Review",
        summary="Beneficial ownership and sanctions note need human confirmation.",
        reviewer="Risk Team",
        priority="medium",
        status="pending_approval",
    ),
]

PROVIDER_HEALTH = [
    ProviderHealth(
        provider="anthropic",
        status="online",
        median_latency="2.3s",
        strongest_for="Document extraction",
    ),
    ProviderHealth(
        provider="openai",
        status="online",
        median_latency="1.8s",
        strongest_for="Policy comparison",
    ),
    ProviderHealth(
        provider="google",
        status="online",
        median_latency="1.4s",
        strongest_for="High-volume summaries",
    ),
]

FILES: list[UploadedFile] = []

app = FastAPI(title="OrbitOps AI API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def run_number() -> str:
    return f"RUN-{1840 + len(RUNS) + 1}"


def file_number() -> str:
    return f"FILE-{240 + len(FILES) + 1}"


def choose_route(submission: TaskSubmission) -> RouteDecision:
    template = next(
        (workflow for workflow in WORKFLOWS if workflow.name == submission.workflow_name),
        None,
    )
    if template is None:
        model = "gpt-4.1-mini" if submission.latency_target == "fast" else "claude-3-5-sonnet"
        fallback = "gemini-2.0-flash"
        reason = "Used default policy route because the workflow template was not found."
    else:
        model = template.primary_model
        fallback = template.fallback_model
        reason = f"Matched workflow policy for {template.task_type} tasks."

        if submission.latency_target == "fast" and model == "claude-3-5-sonnet":
            model = "gpt-4.1-mini"
            fallback = template.primary_model
            reason = "Adjusted primary route for lower latency while preserving fallback coverage."

    review_required = submission.requires_review or (
        template.review_required if template is not None else submission.task_type in {"compare", "extract"}
    )

    return RouteDecision(
        provider=PROVIDER_MAP.get(model, "openai"),
        model=model,
        fallback_model=fallback,
        reason=reason,
        review_required=review_required,
    )


@app.get("/health")
def healthcheck() -> dict[str, str]:
    return {"status": "ok", "service": "orbitops-api", "timestamp": datetime.now(UTC).isoformat()}


@app.get("/dashboard")
def dashboard() -> dict[str, object]:
    return {
        "metrics": {
            "active_workflows": len(WORKFLOWS),
            "providers_online": len(PROVIDER_HEALTH),
            "pending_reviews": len(REVIEW_QUEUE),
            "validation_pass_rate": "98.4%",
            "uploaded_files": len(FILES),
        },
        "runs": RUNS,
        "review_queue": REVIEW_QUEUE,
        "provider_health": PROVIDER_HEALTH,
        "files": FILES,
    }


@app.get("/workflows")
def list_workflows() -> dict[str, list[WorkflowTemplate]]:
    return {"items": WORKFLOWS}


@app.get("/runs")
def list_runs() -> dict[str, list[RunRecord]]:
    return {"items": RUNS}


@app.get("/review")
def list_review_queue() -> dict[str, list[ReviewItem]]:
    return {"items": REVIEW_QUEUE}


@app.get("/providers")
def list_providers() -> dict[str, list[ProviderHealth]]:
    return {"items": PROVIDER_HEALTH}


@app.get("/files")
def list_files() -> dict[str, list[UploadedFile]]:
    return {"items": FILES}


@app.post("/route")
def route_task(submission: TaskSubmission) -> dict[str, RouteDecision]:
    return {"route": choose_route(submission)}


@app.post("/runs/simulate")
def simulate_run(submission: TaskSubmission) -> dict[str, object]:
    route = choose_route(submission)
    outcome = "in_review" if route.review_required else "approved"
    run = RunRecord(
        id=run_number(),
        workflow=submission.workflow_name,
        provider=route.provider,
        model=route.model,
        outcome=outcome,
        submitted_at=datetime.now(UTC).strftime("%I:%M %p"),
    )
    RUNS.insert(0, run)
    if route.review_required:
        REVIEW_QUEUE.insert(
            0,
            ReviewItem(
                id=run.id,
                workflow=submission.workflow_name,
                summary=submission.context[:90],
                reviewer="Operations Review",
                priority="high" if submission.task_type in {"compare", "extract"} else "medium",
                status="open",
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


@app.post("/files")
def create_file(request: FileUploadRequest) -> dict[str, UploadedFile]:
    upload = UploadedFile(
        id=file_number(),
        filename=request.filename,
        content_type=request.content_type,
        workspace=request.workspace,
        uploaded_at=datetime.now(UTC).strftime("%I:%M %p"),
        status="ready",
    )
    FILES.insert(0, upload)
    return {"file": upload}


@app.post("/review/{run_id}")
def review_run(run_id: str, request: ReviewDecisionRequest) -> dict[str, object]:
    queue_item = next((item for item in REVIEW_QUEUE if item.id == run_id), None)
    if queue_item is None:
        raise HTTPException(status_code=404, detail="Review item not found.")

    REVIEW_QUEUE.remove(queue_item)
    run = next((item for item in RUNS if item.id == run_id), None)
    if run is None:
        raise HTTPException(status_code=404, detail="Run not found.")

    updated_outcome = "approved" if request.decision == "approve" else "failed"
    updated_run = run.model_copy(update={"outcome": updated_outcome})
    RUNS[RUNS.index(run)] = updated_run

    return {
        "run": updated_run,
        "decision": {
            "actor": request.actor,
            "note": request.note,
            "status": request.decision,
        },
    }

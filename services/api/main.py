from datetime import datetime
from typing import Literal

from fastapi import FastAPI
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


class RouteDecision(BaseModel):
    provider: str
    model: str
    fallback_model: str
    reason: str
    review_required: bool


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

app = FastAPI(title="OrbitOps AI API", version="0.1.0")


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
    return {"status": "ok", "service": "orbitops-api", "timestamp": datetime.utcnow().isoformat()}


@app.get("/workflows")
def list_workflows() -> dict[str, list[WorkflowTemplate]]:
    return {"items": WORKFLOWS}


@app.post("/route")
def route_task(submission: TaskSubmission) -> dict[str, RouteDecision]:
    return {"route": choose_route(submission)}

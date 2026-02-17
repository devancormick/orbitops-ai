import importlib
import os
from pathlib import Path

from fastapi.testclient import TestClient


def load_client(tmp_path: Path) -> TestClient:
    os.environ["ORBITOPS_DB_PATH"] = str(tmp_path / "test-orbitops.db")
    main = importlib.import_module("main")
    main = importlib.reload(main)
    return TestClient(main.app)


def login_headers(client: TestClient) -> dict[str, str]:
    response = client.post(
        "/auth/login",
        json={"email": "admin@orbitops.local", "password": "orbitops123"},
    )
    assert response.status_code == 200
    token = response.json()["token"]
    return {"x-auth-token": token}


def test_dashboard_returns_metrics(tmp_path: Path):
    client = load_client(tmp_path)
    response = client.get("/dashboard")

    assert response.status_code == 200
    payload = response.json()
    assert "metrics" in payload
    assert "runs" in payload


def test_register_and_login_flow(tmp_path: Path):
    client = load_client(tmp_path)
    register = client.post(
        "/auth/register",
        json={
            "email": "ops@example.com",
            "password": "strongpass1",
            "full_name": "Ops User",
            "workspace": "Operations Workspace",
            "role": "operator",
        },
    )

    assert register.status_code == 200
    login = client.post("/auth/login", json={"email": "ops@example.com", "password": "strongpass1"})
    assert login.status_code == 200
    assert login.json()["user"]["full_name"] == "Ops User"


def test_create_run_creates_review_item_when_required(tmp_path: Path):
    client = load_client(tmp_path)
    headers = login_headers(client)
    response = client.post(
        "/runs",
        headers=headers,
        json={
            "workflow_name": "Vendor Intake Review",
            "task_type": "extract",
            "latency_target": "balanced",
            "requires_review": True,
            "context": "Extract vendor registration details and confirm sanctions references.",
            "workspace": "QA Workspace",
            "uploaded_file_ids": [],
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["run"]["workflow"] == "Vendor Intake Review"
    assert payload["route"]["review_required"] is True

    review_response = client.get("/review")
    assert any(item["id"] == payload["run"]["id"] for item in review_response.json()["items"])


def test_review_run_approves_existing_item(tmp_path: Path):
    client = load_client(tmp_path)
    headers = login_headers(client)
    create_response = client.post(
        "/runs",
        headers=headers,
        json={
            "workflow_name": "Policy Delta Check",
            "task_type": "compare",
            "latency_target": "balanced",
            "requires_review": True,
            "context": "Compare updated policy clauses and hold for legal review.",
            "workspace": "Legal Ops",
            "uploaded_file_ids": [],
        },
    )
    run_id = create_response.json()["run"]["id"]

    review_response = client.post(
        f"/review/{run_id}",
        headers=headers,
        json={"decision": "approve", "actor": "Alex", "note": "Approved after manual clause check."},
    )

    assert review_response.status_code == 200
    assert review_response.json()["run"]["outcome"] == "approved"


def test_file_creation_records_uploaded_file(tmp_path: Path):
    client = load_client(tmp_path)
    headers = login_headers(client)
    response = client.post(
        "/files",
        headers=headers,
        json={
            "filename": "updated-policy.pdf",
            "content_type": "application/pdf",
            "workspace": "Legal Ops",
        },
    )

    assert response.status_code == 200
    assert response.json()["file"]["filename"] == "updated-policy.pdf"


def test_admin_can_create_workflow(tmp_path: Path):
    client = load_client(tmp_path)
    headers = login_headers(client)
    response = client.post(
        "/workflows",
        headers=headers,
        json={
            "name": "Invoice Exception Review",
            "task_type": "classify",
            "primary_model": "gpt-4.1-mini",
            "fallback_model": "claude-3-5-sonnet",
            "review_required": False,
            "workspace": "Finance Ops",
        },
    )

    assert response.status_code == 200
    assert response.json()["workflow"]["name"] == "Invoice Exception Review"

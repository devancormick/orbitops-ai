from fastapi.testclient import TestClient

from main import app


client = TestClient(app)


def test_dashboard_returns_metrics():
    response = client.get("/dashboard")

    assert response.status_code == 200
    payload = response.json()
    assert "metrics" in payload
    assert "runs" in payload


def test_simulate_run_creates_review_item_when_required():
    response = client.post(
        "/runs/simulate",
        json={
            "workflow_name": "Vendor Intake Review",
            "task_type": "extract",
            "latency_target": "balanced",
            "requires_review": True,
            "context": "Extract vendor registration details and confirm sanctions references.",
            "workspace": "QA Workspace",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["run"]["workflow"] == "Vendor Intake Review"
    assert payload["route"]["review_required"] is True

    review_response = client.get("/review")
    assert any(item["id"] == payload["run"]["id"] for item in review_response.json()["items"])


def test_review_run_approves_existing_item():
    create_response = client.post(
        "/runs/simulate",
        json={
            "workflow_name": "Policy Delta Check",
            "task_type": "compare",
            "latency_target": "balanced",
            "requires_review": True,
            "context": "Compare updated policy clauses and hold for legal review.",
            "workspace": "Legal Ops",
        },
    )
    run_id = create_response.json()["run"]["id"]

    review_response = client.post(
        f"/review/{run_id}",
        json={"decision": "approve", "actor": "Alex", "note": "Approved after manual clause check."},
    )

    assert review_response.status_code == 200
    assert review_response.json()["run"]["outcome"] == "approved"


def test_file_creation_records_uploaded_file():
    response = client.post(
        "/files",
        json={
            "filename": "updated-policy.pdf",
            "content_type": "application/pdf",
            "workspace": "Legal Ops",
        },
    )

    assert response.status_code == 200
    assert response.json()["file"]["filename"] == "updated-policy.pdf"

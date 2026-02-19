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


def test_dashboard_returns_contract_metrics(tmp_path: Path):
    client = load_client(tmp_path)
    response = client.get("/dashboard")

    assert response.status_code == 200
    payload = response.json()
    assert "metrics" in payload
    assert "documents" in payload
    assert payload["metrics"]["active_templates"] >= 2


def test_register_and_login_flow(tmp_path: Path):
    client = load_client(tmp_path)
    register = client.post(
        "/auth/register",
        json={
            "email": "ops@example.com",
            "password": "strongpass1",
            "full_name": "Ops User",
            "workspace": "Sunline Realty",
            "role": "agent",
        },
    )

    assert register.status_code == 200
    login = client.post("/auth/login", json={"email": "ops@example.com", "password": "strongpass1"})
    assert login.status_code == 200
    assert login.json()["user"]["full_name"] == "Ops User"


def test_templates_endpoint_returns_seeded_contracts(tmp_path: Path):
    client = load_client(tmp_path)
    response = client.get("/templates")

    assert response.status_code == 200
    names = [item["name"] for item in response.json()["items"]]
    assert "Listing Agreement" in names
    assert "Purchase & Sale Agreement" in names


def test_intake_start_returns_guided_questions(tmp_path: Path):
    client = load_client(tmp_path)
    headers = login_headers(client)
    response = client.post(
        "/intake/start",
        headers=headers,
        json={
            "template_key": "listing-agreement",
            "workspace": "Sunline Realty",
            "agent_name": "Devan Cormick",
            "client_email": "agent@example.com",
            "notes": "Rush listing packet for this week.",
        },
    )

    assert response.status_code == 200
    session = response.json()["session"]
    assert session["template_key"] == "listing-agreement"
    assert len(session["questions"]) >= 5


def test_generate_document_creates_reviewable_record(tmp_path: Path):
    client = load_client(tmp_path)
    headers = login_headers(client)
    response = client.post(
        "/documents/generate",
        headers=headers,
        json={
            "template_key": "purchase-sale-agreement",
            "workspace": "Sunline Realty",
            "agent_name": "Devan Cormick",
            "client_email": "agent@example.com",
            "notes": "Buyer requested same-day draft.",
            "responses": {
                "property_address": "88 Willow Creek Lane, Austin, TX",
                "buyer_name": "Nina Patel",
                "seller_name": "Marcus Bell",
                "purchase_price": "$540,000",
                "closing_date": "2026-03-31",
                "earnest_money": "$8,000",
            },
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["document"]["template_name"] == "Purchase & Sale Agreement"
    assert payload["document"]["field_values"]["buyer_name"] == "Nina Patel"
    assert payload["delivery"]["download_ready"] is True


def test_email_and_download_actions_succeed(tmp_path: Path):
    client = load_client(tmp_path)
    headers = login_headers(client)
    create_response = client.post(
        "/documents/generate",
        headers=headers,
        json={
            "template_key": "listing-agreement",
            "workspace": "Sunline Realty",
            "agent_name": "Devan Cormick",
            "client_email": "agent@example.com",
            "notes": "",
            "responses": {
                "property_address": "14 Cedar Point, Franklin, TN",
                "seller_name": "Olivia Hayes",
                "listing_price": "$720,000",
                "listing_start_date": "2026-03-20",
                "listing_end_date": "2026-09-20",
                "commission_rate": "6%",
            },
        },
    )
    document_id = create_response.json()["document"]["id"]

    email_response = client.post(
        f"/documents/{document_id}/email",
        headers=headers,
        json={"email": "olivia@example.com"},
    )
    download_response = client.post(
        f"/documents/{document_id}/download",
        headers=headers,
    )

    assert email_response.status_code == 200
    assert email_response.json()["delivery"]["status"] == "sent_demo"
    assert download_response.status_code == 200
    assert download_response.json()["delivery"]["status"] == "downloaded_demo"


def test_admin_can_create_template(tmp_path: Path):
    client = load_client(tmp_path)
    headers = login_headers(client)
    response = client.post(
        "/templates",
        headers=headers,
        json={
            "name": "Lease Renewal Agreement",
            "template_key": "lease-renewal-agreement",
            "description": "Simple lease renewal workflow for extensions and updated rent terms.",
            "agreement_type": "listing_agreement",
            "review_required": False,
            "workspace": "Sunline Realty",
            "fields": [
                {
                    "key": "property_address",
                    "label": "Property address",
                    "question": "What property address should appear on the renewal?",
                    "required": True,
                }
            ],
        },
    )

    assert response.status_code == 200
    assert response.json()["template"]["name"] == "Lease Renewal Agreement"

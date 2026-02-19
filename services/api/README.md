# OrbitOps API

FastAPI service for the real estate contract generator demo. It handles template management, guided intake, document generation, simulated delivery, and local auth.

## Available endpoints

- `POST /auth/register`
- `POST /auth/login`
- `GET /dashboard`
- `GET /health`
- `GET /templates`
- `POST /templates`
- `POST /intake/start`
- `POST /documents/generate`
- `GET /documents`
- `POST /documents/{document_id}/email`
- `POST /documents/{document_id}/download`

## Run locally

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

Open `http://127.0.0.1:8000/docs` for the interactive FastAPI docs.

Seeded local admin credentials:

- email: `admin@orbitops.local`
- password: `orbitops123`

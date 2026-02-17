# OrbitOps API

FastAPI service for workflow routing, provider selection, validation hooks, and execution audit primitives.

## Available endpoints

- `POST /auth/register`
- `POST /auth/login`
- `GET /health`
- `GET /dashboard`
- `GET /workflows`
- `POST /workflows`
- `GET /runs`
- `POST /runs`
- `GET /review`
- `POST /review/{run_id}`
- `GET /providers`
- `GET /files`
- `POST /files`
- `POST /route`
- `POST /runs/simulate`

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

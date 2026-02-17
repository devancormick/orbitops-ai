# OrbitOps API

FastAPI service for workflow routing, provider selection, validation hooks, and execution audit primitives.

## Available endpoints

- `GET /health`
- `GET /dashboard`
- `GET /workflows`
- `GET /runs`
- `GET /review`
- `GET /providers`
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

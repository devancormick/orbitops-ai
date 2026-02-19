# OrbitOps AI

OrbitOps AI is a private, portfolio-style real estate contract generator demo. It presents a lightweight SaaS workflow where an AI-guided assistant collects deal details from an agent, maps those answers into structured fields, and prepares finished agreement packets for preview, download, and email delivery.

The repository is intentionally framed like a prior client build rather than a generic sandbox. The focus is practical document automation: guided intake, template management, PDF-ready output, and a simple admin layer that keeps the system easy to demo and easy to extend.

## Product Overview

The app walks a real estate agent through the information needed to produce agreements such as Listing Agreements and Purchase & Sale Agreements. Instead of dropping users into an open chat box, the system stages the conversation around required contract fields, validates the captured data, and assembles a finished document record that can be reviewed or shared immediately.

## Core Capabilities

- AI-guided contract intake for real estate agents
- Structured field capture for sellers, buyers, property details, price, dates, and commission
- Template-driven agreement generation for multiple contract types
- Preview, download, and email flows for completed documents
- Admin controls for enabling and adjusting contract templates
- Lightweight persistence through FastAPI and SQLite for a demo-friendly local setup

## Architecture

- `apps/web`: Next.js application for the agent intake flow, document preview, admin tools, and authentication
- `services/api`: FastAPI backend for templates, intake sessions, document generation, simulated delivery, and local persistence
- `packages/shared`: shared seed data and contract template metadata used by the demo

## Included Demo Scope

The repository includes a working scaffold for:

- contract template browsing
- AI-style guided intake
- generated document previews
- download and email simulation
- template administration
- seeded auth for local review

The implementation is intentionally lightweight, but it is structured like a credible MVP that can be shown in a proposal or expanded into a production build.

## MVP Coverage

- Listing Agreement template
- Purchase & Sale Agreement template
- Agent-facing intake flow with structured prompts
- Generated agreement preview with field summary
- Download and email actions in demo mode
- Admin template form for adding or adjusting templates
- FastAPI endpoints for templates, intake, generation, delivery, and auth

## Product Screens

These visuals remain helpful as lightweight repository screenshots while the product is positioned around contract automation.

### Dashboard Overview

Shows the main workspace and generated agreement activity.

![OrbitOps dashboard overview](assets/screenshots/dashboard-overview.svg)

### Routing Center

Shows how the assistant-guided intake becomes a structured document workflow.

![OrbitOps routing center](assets/screenshots/routing-center.svg)

### Review Queue

Shows documents awaiting human approval before final delivery.

![OrbitOps review queue](assets/screenshots/review-queue.svg)

## Local Development

### Web

```bash
npm install
npm run dev:web
```

### API

```bash
cd services/api
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

Current API surface:

- `POST /auth/register`
- `POST /auth/login`
- `GET /dashboard`
- `GET /templates`
- `POST /templates`
- `POST /intake/start`
- `POST /documents/generate`
- `GET /documents`
- `POST /documents/{document_id}/email`
- `POST /documents/{document_id}/download`

Seeded local admin account:

- email: `admin@orbitops.local`
- password: `orbitops123`

## Why This Project Exists

This repository is meant to package a believable prior solution for an operator-led client who needs a simple AI document generator, not a research-heavy AI stack. The emphasis is on reliability, structured capture, and fast MVP delivery instead of complex orchestration or hype-driven architecture.

## Repository Status

This repository is private and intended for controlled development, proposal support, and portfolio-style packaging only.

## License

Private and proprietary. All rights reserved.

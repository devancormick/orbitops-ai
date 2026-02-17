# OrbitOps AI MVP Plan

## Summary

OrbitOps AI is a multi-AI operations workflow hub for teams that need document intake, task routing, structured outputs, review checkpoints, and provider flexibility in one product. The MVP is designed as a real platform blueprint rather than a demo chatbot or a no-code automation wrapper.

The system should feel similar to a custom AI platform a client would request, but be differentiated by a stronger operations focus, better governance, and a workflow-driven model instead of a generic chat interface.

## Product Goals

- Give teams a single workspace to run repeatable AI-assisted operational workflows
- Route tasks to different AI providers based on workflow needs and policy rules
- Capture structured outputs that can be reviewed, approved, and reused
- Keep full run history, provider decisions, error traces, and fallback behavior visible
- Support future growth through modular provider adapters and configurable workflow templates

## Intended Stack

### Frontend

- Next.js for authentication flows, dashboard screens, workflow submission, result review, and file upload UX

### Backend

- Python API and orchestration service for workflow execution, provider abstraction, prompt handling, schema validation, fallback routing, retries, and logging

### Database

- PostgreSQL for persistent storage across users, workspaces, workflows, files, runs, outputs, approvals, and audit logs

## Intended Repository Structure

- `apps/web`
  - dashboard application
  - auth screens
  - workflow submission UI
  - file upload views
  - run history and review queue
- `services/api`
  - orchestration service
  - provider adapters
  - workflow executor
  - schema validation
  - logging and fallback modules
- `packages/shared`
  - workflow definitions
  - request and response contracts
  - result schemas
  - shared enums and policy types

## Core Entities

- `User`: authenticated platform user with role and workspace memberships
- `Workspace`: team or client environment that owns workflows, files, and run history
- `WorkflowTemplate`: reusable task definition with input requirements, output schema, routing policy, and review requirements
- `TaskRun`: execution record for a workflow submission, including status, timestamps, provider choice, and fallback path
- `UploadedFile`: source file record with storage metadata, processing status, and task associations
- `ModelRoute`: routing decision record showing why a provider and model were selected
- `StructuredResult`: validated output payload linked to a completed task run
- `ReviewDecision`: approval or rejection action taken by a human reviewer
- `AuditLog`: append-only event trail for system actions, model usage, errors, and review changes

## Core Features

### Authentication and Accounts

- Support user registration, sign-in, session handling, and role-based access
- Associate users with one or more workspaces
- Restrict review and admin capabilities by role

### Workspace Dashboard

- Show active workflows, recent task runs, pending reviews, and recent uploads
- Surface model usage summaries and task status counts
- Provide quick entry points for starting new workflow runs

### Workflow-Based Task Submission

- Let users select a workflow template such as summarize, extract, classify, compare, or draft
- Collect structured inputs for each workflow type
- Attach files and metadata to the task submission

### Multi-Provider Routing Engine

- Choose provider and model based on workflow type, required output format, latency target, cost sensitivity, and fallback rules
- Keep routing logic policy-driven so new providers can be added without rewriting the entire execution layer
- Record route decisions for later analysis and debugging

### Prompt Handling and Structured Outputs

- Version prompt templates per workflow
- Enforce JSON or schema-based outputs when required
- Validate outputs before marking a task as successful
- Return invalid outputs to retry or fallback flows when appropriate

### File Upload and Processing

- Accept operational documents and internal files tied to a workflow run
- Store file metadata and processing state
- Prepare extracted text or derived artifacts for model execution pipelines

### Fallback Logic and Error Handling

- Retry transient failures
- Switch to alternate providers or models when a primary route fails
- Persist execution errors, retry attempts, and fallback outcomes

### Review and Approval Queue

- Route sensitive or high-impact tasks into a human review queue
- Allow reviewers to approve, reject, or request re-run
- Preserve review decisions in the run history

### Auditability and Observability

- Log task lifecycle events from submission through completion
- Track provider latency, failure rate, and output quality flags
- Make it possible to inspect why a route was chosen and what happened during execution

## Better-Than-Client Additions

- Admin-configurable workflow templates instead of hardcoded task definitions
- Approval checkpoints for regulated or business-critical workflows
- Provider performance logging to improve routing over time
- Traceable result history by workflow, workspace, model, and reviewer
- Policy-based routing that can evolve into governance controls later

## Delivery Phases

### Phase 1: Foundation

- Set up repo structure, local development standards, and shared contracts
- Define the database schema for users, workspaces, workflows, files, runs, outputs, and reviews
- Establish auth and workspace concepts

### Phase 2: Orchestration Layer

- Build provider adapter interface and first provider integrations
- Implement workflow executor, route policy evaluation, prompt template loading, output validation, and fallback behavior
- Add run logging and audit event capture

### Phase 3: Product Interface

- Build dashboard, workflow submission forms, run history, and review queue in Next.js
- Connect UI flows to the orchestration API
- Add upload flows and result inspection views

### Phase 4: Governance and Hardening

- Add admin workflow management
- Expand observability and provider performance reporting
- Tighten role-based permissions, retry policies, and review controls

## Acceptance Criteria

- A signed-in user can create a task run from a workflow template
- A task run can include uploaded files and structured inputs
- The system chooses a provider route based on workflow rules
- The output is validated and stored as a structured result
- Failures trigger retries or fallback routes and are fully logged
- Review-required workflows appear in a human approval queue
- Workspace users can inspect run history, route choices, and final outcomes

## Notes

OrbitOps AI should remain clearly distinct from a generic chatbot product. The interface and backend design should center on operational workflows, traceability, and governance so the project reads as a mature previous-client platform rather than a direct copy of a current opportunity.

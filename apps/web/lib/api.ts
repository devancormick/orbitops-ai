import { providerHealth, reviewQueue, runHistory, workflows } from "./data";

export type DashboardPayload = {
  metrics: {
    active_workflows: number;
    providers_online: number;
    pending_reviews: number;
    validation_pass_rate: string;
    uploaded_files?: number;
  };
  runs: Array<{
    id: string;
    workflow: string;
    provider: string;
    model: string;
    outcome: string;
    submitted_at: string;
  }>;
  review_queue: Array<{
    id: string;
    workflow: string;
    summary: string;
    reviewer: string;
    priority: string;
    status: string;
    age?: string;
  }>;
  provider_health: Array<{
    provider: string;
    status: string;
    median_latency: string;
    strongest_for: string;
  }>;
};

const API_URL = process.env.NEXT_PUBLIC_API_URL;

async function fetchJson<T>(path: string): Promise<T | null> {
  if (!API_URL) {
    return null;
  }

  try {
    const response = await fetch(`${API_URL}${path}`, { cache: "no-store" });
    if (!response.ok) {
      return null;
    }
    return (await response.json()) as T;
  } catch {
    return null;
  }
}

export async function getDashboardData(): Promise<DashboardPayload> {
  const payload = await fetchJson<DashboardPayload>("/dashboard");

  if (payload) {
    return payload;
  }

  return {
    metrics: {
      active_workflows: workflows.length,
      providers_online: providerHealth.length,
      pending_reviews: reviewQueue.length,
      validation_pass_rate: "98.4%",
      uploaded_files: 0
    },
    runs: runHistory.map((run) => ({
      id: run.id,
      workflow: run.workflow,
      provider: run.provider,
      model: run.model,
      outcome: run.outcome,
      submitted_at: run.submittedAt
    })),
    review_queue: reviewQueue.map((item) => ({
      id: item.id,
      workflow: item.workflow,
      summary: item.summary,
      reviewer: item.reviewer,
      priority: item.priority,
      status: "open",
      age: item.age
    })),
    provider_health: providerHealth.map((provider) => ({
      provider: provider.name,
      status: provider.status.toLowerCase(),
      median_latency: provider.latency,
      strongest_for: provider.strength
    }))
  };
}

export async function submitRun(payload: {
  workflow_name: string;
  task_type: string;
  latency_target: string;
  requires_review: boolean;
  context: string;
  workspace: string;
}) {
  if (!API_URL) {
    return {
      ok: true,
      run: {
        id: "RUN-DEMO",
        workflow: payload.workflow_name,
        outcome: payload.requires_review ? "in_review" : "approved"
      }
    };
  }

  const response = await fetch(`${API_URL}/runs/simulate`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(payload)
  });

  if (!response.ok) {
    return { ok: false };
  }

  return { ok: true, ...(await response.json()) };
}

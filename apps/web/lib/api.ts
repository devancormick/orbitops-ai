import { documentHistory, reviewQueue, templates } from "./data";

export type DashboardPayload = {
  metrics: {
    active_templates: number;
    generated_documents: number;
    pending_reviews: number;
    delivery_readiness: string;
  };
  documents: typeof documentHistory;
  review_queue: typeof reviewQueue;
};

const API_URL = process.env.NEXT_PUBLIC_API_URL;
const TOKEN_KEY = "orbitops-token";

type TemplatePayload = (typeof templates)[number];
type DocumentPayload = (typeof documentHistory)[number];

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

function getToken(): string | null {
  if (typeof window === "undefined") {
    return null;
  }
  return window.localStorage.getItem(TOKEN_KEY);
}

export function storeToken(token: string) {
  if (typeof window !== "undefined") {
    window.localStorage.setItem(TOKEN_KEY, token);
  }
}

export function clearToken() {
  if (typeof window !== "undefined") {
    window.localStorage.removeItem(TOKEN_KEY);
  }
}

async function authedJson(path: string, payload?: object) {
  if (!API_URL) {
    return null;
  }
  const token = getToken();
  const response = await fetch(`${API_URL}${path}`, {
    method: payload ? "POST" : "GET",
    headers: {
      "Content-Type": "application/json",
      ...(token ? { "x-auth-token": token } : {})
    },
    ...(payload ? { body: JSON.stringify(payload) } : {})
  });
  if (!response.ok) {
    return null;
  }
  return response.json();
}

export async function getDashboardData(): Promise<DashboardPayload> {
  const payload = await fetchJson<DashboardPayload>("/dashboard");
  if (payload) {
    return payload;
  }

  return {
    metrics: {
      active_templates: templates.length,
      generated_documents: documentHistory.length,
      pending_reviews: reviewQueue.length,
      delivery_readiness: "Demo ready"
    },
    documents: documentHistory,
    review_queue: reviewQueue
  };
}

export async function getTemplates(): Promise<TemplatePayload[]> {
  const payload = await fetchJson<{ items: TemplatePayload[] }>("/templates");
  return payload?.items ?? templates;
}

export async function getDocuments(): Promise<DocumentPayload[]> {
  const payload = await fetchJson<{ items: DocumentPayload[] }>("/documents");
  return payload?.items ?? documentHistory;
}

export async function login(payload: { email: string; password: string }) {
  if (!API_URL) {
    return { ok: true, token: "demo-token", user: { full_name: "D. Cormick" } };
  }
  const response = await fetch(`${API_URL}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });
  if (!response.ok) {
    return { ok: false };
  }
  return { ok: true, ...(await response.json()) };
}

export async function startIntake(payload: {
  template_key: string;
  workspace: string;
  agent_name: string;
  client_email: string;
  notes: string;
}) {
  if (!API_URL) {
    const selected = templates.find((item) => item.template_key === payload.template_key) ?? templates[0];
    return {
      ok: true,
      session: {
        id: "INTAKE-1001",
        template_key: payload.template_key,
        agent_name: payload.agent_name,
        client_email: payload.client_email,
        workspace: payload.workspace,
        assistant_prompt: `I will help prepare the ${selected.name} by collecting the required deal fields one at a time.`,
        questions: selected.fields
      }
    };
  }

  const result = await authedJson("/intake/start", payload);
  if (!result) {
    return { ok: false };
  }
  return { ok: true, ...result };
}

export async function generateDocument(payload: {
  template_key: string;
  workspace: string;
  agent_name: string;
  client_email: string;
  notes: string;
  responses: Record<string, string>;
}) {
  if (!API_URL) {
    const selected = templates.find((item) => item.template_key === payload.template_key) ?? templates[0];
    return {
      ok: true,
      document: {
        id: "DOC-DEMO",
        template_name: selected.name,
        template_key: selected.template_key,
        agreement_type: selected.agreement_type,
        workspace: payload.workspace,
        status: selected.review_required ? "pending_review" : "ready",
        generated_at: "10:18 AM",
        requested_by: payload.agent_name,
        recipient_email: payload.client_email,
        preview_title: `${selected.name} for ${payload.responses.property_address ?? "the property"}`,
        summary: `${selected.name} prepared for ${payload.responses.seller_name ?? payload.responses.buyer_name ?? "the client"}.`,
        field_values: payload.responses,
        preview_markdown: `# ${selected.name}`,
        email_status: "not_sent",
        download_status: "ready"
      },
      delivery: {
        download_ready: true,
        email_ready: true,
        mode: "demo"
      }
    };
  }

  const result = await authedJson("/documents/generate", payload);
  if (!result) {
    return { ok: false };
  }
  return { ok: true, ...result };
}

export async function sendDocumentEmail(documentId: string, email: string) {
  if (!API_URL) {
    return { ok: true, delivery: { channel: "email", status: "sent_demo", email } };
  }
  const result = await authedJson(`/documents/${documentId}/email`, { email });
  if (!result) {
    return { ok: false };
  }
  return { ok: true, ...result };
}

export async function downloadDocument(documentId: string) {
  if (!API_URL) {
    return { ok: true, delivery: { channel: "download", status: "downloaded_demo", filename: `${documentId}.pdf` } };
  }
  const result = await authedJson(`/documents/${documentId}/download`, {});
  if (!result) {
    return { ok: false };
  }
  return { ok: true, ...result };
}

export async function createTemplate(payload: {
  name: string;
  template_key: string;
  description: string;
  agreement_type: "listing_agreement" | "purchase_sale_agreement";
  review_required: boolean;
  workspace: string;
  fields: Array<{ key: string; label: string; question: string; required: boolean }>;
}) {
  if (!API_URL) {
    return { ok: true, template: { ...payload, active: true } };
  }
  const result = await authedJson("/templates", payload);
  if (!result) {
    return { ok: false };
  }
  return { ok: true, ...result };
}

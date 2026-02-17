export type Workflow = {
  name: string;
  taskType: "summarize" | "extract" | "classify" | "compare" | "draft";
  goal: string;
  route: string;
  status: "Healthy" | "Needs review" | "Watching";
  reviewRequired: boolean;
  volume: string;
};

export type RunRecord = {
  id: string;
  workflow: string;
  model: string;
  provider: string;
  outcome: "approved" | "in review" | "fallback used" | "failed";
  submittedAt: string;
};

export type ReviewItem = {
  id: string;
  workflow: string;
  priority: "High" | "Medium";
  summary: string;
  reviewer: string;
  age: string;
};

export const workflows: Workflow[] = [
  {
    name: "Vendor Intake Review",
    taskType: "extract",
    goal: "Extract registration data, flag risk markers, and draft onboarding notes.",
    route: "Claude Sonnet -> GPT-4.1 mini fallback",
    status: "Healthy",
    reviewRequired: true,
    volume: "42 runs this week"
  },
  {
    name: "Policy Delta Check",
    taskType: "compare",
    goal: "Compare policy revisions, classify changes, and prepare legal ops summaries.",
    route: "GPT-4.1 -> Gemini 2.0 Flash fallback",
    status: "Needs review",
    reviewRequired: true,
    volume: "18 runs this week"
  },
  {
    name: "Claims Summary Queue",
    taskType: "summarize",
    goal: "Condense claim packs into investigator-ready structured briefs.",
    route: "Gemini 2.0 Flash -> Claude Sonnet fallback",
    status: "Healthy",
    reviewRequired: false,
    volume: "67 runs this week"
  },
  {
    name: "Partner SLA Classifier",
    taskType: "classify",
    goal: "Classify inbound support escalations by SLA tier and response ownership.",
    route: "GPT-4.1 mini -> Claude Sonnet fallback",
    status: "Watching",
    reviewRequired: false,
    volume: "109 runs this week"
  }
];

export const runHistory: RunRecord[] = [
  {
    id: "RUN-1842",
    workflow: "Vendor Intake Review",
    model: "claude-3-5-sonnet",
    provider: "anthropic",
    outcome: "approved",
    submittedAt: "08:31 AM"
  },
  {
    id: "RUN-1841",
    workflow: "Policy Delta Check",
    model: "gpt-4.1",
    provider: "openai",
    outcome: "in review",
    submittedAt: "08:12 AM"
  },
  {
    id: "RUN-1839",
    workflow: "Claims Summary Queue",
    model: "gemini-2.0-flash",
    provider: "google",
    outcome: "fallback used",
    submittedAt: "07:44 AM"
  },
  {
    id: "RUN-1835",
    workflow: "Partner SLA Classifier",
    model: "gpt-4.1-mini",
    provider: "openai",
    outcome: "approved",
    submittedAt: "07:03 AM"
  }
];

export const reviewQueue: ReviewItem[] = [
  {
    id: "RUN-1841",
    workflow: "Policy Delta Check",
    priority: "High",
    summary: "3 clauses changed indemnity language and one notice window tightened.",
    reviewer: "Legal Ops",
    age: "12 min"
  },
  {
    id: "RUN-1838",
    workflow: "Vendor Intake Review",
    priority: "Medium",
    summary: "Sanctions note and beneficial ownership section need human confirmation.",
    reviewer: "Risk Team",
    age: "24 min"
  }
];

export const providerHealth = [
  { name: "Anthropic", status: "Online", latency: "2.3s", strength: "Extraction" },
  { name: "OpenAI", status: "Online", latency: "1.8s", strength: "Comparison" },
  { name: "Google", status: "Online", latency: "1.4s", strength: "High-volume summaries" }
];

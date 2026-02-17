const workflows = [
  {
    name: "Vendor Intake Review",
    goal: "Extract fields, classify risk, and draft onboarding notes.",
    route: "Claude Sonnet -> GPT-4.1 fallback",
    status: "Healthy"
  },
  {
    name: "Policy Delta Check",
    goal: "Compare updated policies and flag action items for legal ops.",
    route: "GPT-4.1 -> Gemini 2.0 fallback",
    status: "Needs review"
  },
  {
    name: "Claims Summary Queue",
    goal: "Summarize uploaded claim packs into structured investigator briefs.",
    route: "Gemini 2.0 -> Claude Sonnet fallback",
    status: "Healthy"
  }
];

const runHistory = [
  { id: "RUN-1842", workflow: "Vendor Intake Review", model: "claude-3-5-sonnet", outcome: "approved" },
  { id: "RUN-1841", workflow: "Policy Delta Check", model: "gpt-4.1", outcome: "in review" },
  { id: "RUN-1839", workflow: "Claims Summary Queue", model: "gemini-2.0-flash", outcome: "fallback used" }
];

export default function HomePage() {
  return (
    <main className="shell">
      <section className="hero">
        <div className="hero-copy">
          <p className="eyebrow">Private operations platform</p>
          <h1>OrbitOps AI turns document-heavy team workflows into governed multi-model runs.</h1>
          <p className="lede">
            Route each task to the right model, validate structured outputs, and move sensitive work
            through a human review queue without losing context.
          </p>
          <div className="hero-actions">
            <a href="#workflows" className="button button-primary">View workflows</a>
            <a href="#architecture" className="button button-secondary">See architecture</a>
          </div>
        </div>
        <div className="hero-panel">
          <h2>Live ops snapshot</h2>
          <ul>
            <li><strong>12</strong> active workflows</li>
            <li><strong>3</strong> providers online</li>
            <li><strong>98.4%</strong> validation pass rate this week</li>
            <li><strong>17</strong> approvals pending</li>
          </ul>
        </div>
      </section>

      <section id="workflows" className="section">
        <div className="section-heading">
          <p className="eyebrow">Workflow templates</p>
          <h2>Built for repeatable operations work, not generic chat.</h2>
        </div>
        <div className="card-grid">
          {workflows.map((workflow) => (
            <article key={workflow.name} className="card">
              <p className="card-status">{workflow.status}</p>
              <h3>{workflow.name}</h3>
              <p>{workflow.goal}</p>
              <p className="muted">{workflow.route}</p>
            </article>
          ))}
        </div>
      </section>

      <section className="section split">
        <div className="card">
          <p className="eyebrow">Recent runs</p>
          <h2>Trace every output back to the workflow, provider, and review decision.</h2>
          <div className="run-list">
            {runHistory.map((run) => (
              <div key={run.id} className="run-row">
                <div>
                  <strong>{run.id}</strong>
                  <p>{run.workflow}</p>
                </div>
                <div>
                  <span>{run.model}</span>
                  <p>{run.outcome}</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div id="architecture" className="card dark-card">
          <p className="eyebrow">Architecture</p>
          <h2>Next.js dashboard, Python orchestration, PostgreSQL state.</h2>
          <p>
            The web layer handles intake, review, and visibility. The API layer owns provider routing,
            schema validation, fallback logic, and audit trails across every run.
          </p>
        </div>
      </section>
    </main>
  );
}

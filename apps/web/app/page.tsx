import { Navigation } from "../components/nav";
import { workflows } from "../lib/data";
import { getDashboardData } from "../lib/api";

export default async function HomePage() {
  const dashboard = await getDashboardData();
  return (
    <>
      <Navigation />
      <main className="shell stack">
        <section className="hero">
          <div className="hero-copy">
            <p className="eyebrow">Private operations platform</p>
            <h1>OrbitOps AI turns document-heavy team workflows into governed multi-model runs.</h1>
            <p className="lede">
              Route each task to the right model, validate structured outputs, and move sensitive work
              through a human review queue without losing context.
            </p>
            <div className="hero-actions">
              <a href="/workflows" className="button button-primary">View workflows</a>
              <a href="/submit" className="button button-secondary">Start a run</a>
            </div>
          </div>
          <div className="hero-panel">
            <h2>Live ops snapshot</h2>
            <ul>
              <li><strong>{dashboard.metrics.active_workflows}</strong> active workflows</li>
              <li><strong>{dashboard.metrics.providers_online}</strong> providers online</li>
              <li><strong>{dashboard.metrics.validation_pass_rate}</strong> validation pass rate this week</li>
              <li><strong>{dashboard.metrics.pending_reviews}</strong> approvals waiting now</li>
            </ul>
          </div>
        </section>

        <section className="section">
          <div className="section-heading">
            <p className="eyebrow">Workflow templates</p>
            <h2>Built for repeatable operations work, not generic chat.</h2>
          </div>
          <div className="card-grid">
            {workflows.slice(0, 3).map((workflow) => (
              <article key={workflow.name} className="card">
                <p className="card-status">{workflow.status}</p>
                <h3>{workflow.name}</h3>
                <p>{workflow.goal}</p>
                <p className="muted">{workflow.route}</p>
              </article>
            ))}
          </div>
        </section>

        <section className="split">
          <div className="card">
            <p className="eyebrow">Recent runs</p>
            <h2>Trace every output back to the workflow, provider, and review decision.</h2>
            <div className="run-list">
              {dashboard.runs.map((run) => (
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

          <div className="card dark-card">
            <p className="eyebrow">Architecture</p>
            <h2>Next.js dashboard, Python orchestration, PostgreSQL state.</h2>
            <p>
              The web layer handles intake, review, and visibility. The API layer owns provider routing,
              schema validation, fallback logic, and audit trails across every run.
            </p>
          </div>
        </section>
      </main>
    </>
  );
}

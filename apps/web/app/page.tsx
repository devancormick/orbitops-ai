import { Navigation } from "../components/nav";
import { getDashboardData, getTemplates } from "../lib/api";

export default async function HomePage() {
  const dashboard = await getDashboardData();
  const templates = await getTemplates();

  return (
    <>
      <Navigation />
      <main className="shell stack">
        <section className="hero">
          <div className="hero-copy">
            <p className="eyebrow">Private contract generator</p>
            <h1>OrbitOps AI helps agents turn guided intake answers into ready-to-review real estate agreements.</h1>
            <p className="lede">
              The demo focuses on practical document automation: collect the deal facts, fill the right template,
              preview the agreement, and simulate download or email delivery without production infrastructure.
            </p>
            <div className="hero-actions">
              <a href="/workflows" className="button button-primary">View templates</a>
              <a href="/submit" className="button button-secondary">Start intake</a>
            </div>
          </div>
          <div className="hero-panel">
            <h2>Live demo snapshot</h2>
            <ul>
              <li><strong>{dashboard.metrics.active_templates}</strong> active templates</li>
              <li><strong>{dashboard.metrics.generated_documents}</strong> generated documents</li>
              <li><strong>{dashboard.metrics.pending_reviews}</strong> approvals waiting now</li>
              <li><strong>{dashboard.metrics.delivery_readiness}</strong> delivery mode</li>
            </ul>
          </div>
        </section>

        <section className="section">
          <div className="section-heading">
            <p className="eyebrow">Contract templates</p>
            <h2>Built for guided document completion, not generic chatbot prompts.</h2>
          </div>
          <div className="card-grid">
            {templates.map((template) => (
              <article key={template.template_key} className="card">
                <p className="card-status">{template.review_required ? "Broker review" : "Auto ready"}</p>
                <h3>{template.name}</h3>
                <p>{template.description}</p>
                <p className="muted">{template.fields.length} guided fields</p>
              </article>
            ))}
          </div>
        </section>

        <section className="split">
          <div className="card">
            <p className="eyebrow">Recent agreements</p>
            <h2>Every generated packet stays tied to its template, field values, and delivery status.</h2>
            <div className="run-list">
              {dashboard.documents.map((document) => (
                <div key={document.id} className="run-row">
                  <div>
                    <strong>{document.id}</strong>
                    <p>{document.template_name}</p>
                  </div>
                  <div>
                    <span>{document.status}</span>
                    <p>{document.generated_at}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="card dark-card">
            <p className="eyebrow">MVP stack</p>
            <h2>Next.js dashboard, FastAPI contract engine, SQLite demo state.</h2>
            <p>
              The web layer handles template browsing, guided intake, preview, and admin controls. The API layer
              stores templates, validates required fields, generates document records, and simulates email or PDF delivery.
            </p>
          </div>
        </section>
      </main>
    </>
  );
}

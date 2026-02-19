import { Navigation } from "../../components/nav";
import { getTemplates } from "../../lib/api";

export default async function WorkflowsPage() {
  const templates = await getTemplates();

  return (
    <>
      <Navigation />
      <main className="shell stack">
        <section className="section-heading">
          <p className="eyebrow">Contract templates</p>
          <h1 className="page-title">Configured agreement flows for listings, purchases, and future expansion.</h1>
        </section>
        <section className="card-grid">
          {templates.map((template) => (
            <article key={template.template_key} className="card">
              <div className="pill-row">
                <span className="pill">{template.agreement_type.replace(/_/g, " ")}</span>
                <span className="pill pill-healthy">{template.review_required ? "Review required" : "Ready"}</span>
              </div>
              <h2>{template.name}</h2>
              <p>{template.description}</p>
              <p className="muted">{template.workspace}</p>
              <div className="detail-row">
                <span>{template.fields.length} contract fields</span>
                <span>{template.review_required ? "Broker review" : "Auto-deliver"}</span>
              </div>
            </article>
          ))}
        </section>
      </main>
    </>
  );
}

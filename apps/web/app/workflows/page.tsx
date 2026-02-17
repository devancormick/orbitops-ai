import { Navigation } from "../../components/nav";
import { workflows } from "../../lib/data";

export default function WorkflowsPage() {
  return (
    <>
      <Navigation />
      <main className="shell stack">
        <section className="section-heading">
          <p className="eyebrow">Workflow templates</p>
          <h1 className="page-title">Configured workflows by task type, routing policy, and review rule.</h1>
        </section>
        <section className="card-grid">
          {workflows.map((workflow) => (
            <article key={workflow.name} className="card">
              <div className="pill-row">
                <span className="pill">{workflow.taskType}</span>
                <span className={`pill pill-${workflow.status.toLowerCase().replace(" ", "-")}`}>
                  {workflow.status}
                </span>
              </div>
              <h2>{workflow.name}</h2>
              <p>{workflow.goal}</p>
              <p className="muted">{workflow.route}</p>
              <div className="detail-row">
                <span>{workflow.volume}</span>
                <span>{workflow.reviewRequired ? "Reviewer required" : "Auto-complete allowed"}</span>
              </div>
            </article>
          ))}
        </section>
      </main>
    </>
  );
}

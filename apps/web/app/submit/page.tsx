import { Navigation } from "../../components/nav";
import { workflows } from "../../lib/data";

export default function SubmitPage() {
  return (
    <>
      <Navigation />
      <main className="shell stack">
        <section className="section-heading">
          <p className="eyebrow">New run</p>
          <h1 className="page-title">Start a workflow with structured inputs, review rules, and route intent.</h1>
        </section>
        <section className="split">
          <form className="card form-card">
            <label className="field">
              <span>Workflow template</span>
              <select defaultValue={workflows[0].name}>
                {workflows.map((workflow) => (
                  <option key={workflow.name} value={workflow.name}>
                    {workflow.name}
                  </option>
                ))}
              </select>
            </label>
            <label className="field">
              <span>Latency target</span>
              <select defaultValue="balanced">
                <option value="fast">Fast</option>
                <option value="balanced">Balanced</option>
                <option value="thorough">Thorough</option>
              </select>
            </label>
            <label className="field">
              <span>Request context</span>
              <textarea
                rows={6}
                defaultValue="Upload updated vendor registration documents and extract ownership, sanctions, and onboarding notes."
              />
            </label>
            <div className="action-row">
              <button className="button button-primary" type="submit">Queue run</button>
              <button className="button button-secondary" type="button">Save draft</button>
            </div>
          </form>
          <article className="card">
            <p className="eyebrow">Expected output</p>
            <h2>Structured, traceable, review-ready.</h2>
            <ul className="plain-list">
              <li>Route selected by workflow policy and latency target</li>
              <li>Schema-validated output stored with the run record</li>
              <li>Fallback path preserved if the primary model fails</li>
              <li>Approval queue triggered automatically when needed</li>
            </ul>
          </article>
        </section>
      </main>
    </>
  );
}

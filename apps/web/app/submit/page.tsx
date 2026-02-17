import { Navigation } from "../../components/nav";
import { SubmitForm } from "../../components/submit-form";

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
          <SubmitForm />
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

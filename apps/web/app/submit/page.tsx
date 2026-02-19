import { Navigation } from "../../components/nav";
import { SubmitForm } from "../../components/submit-form";

export default function SubmitPage() {
  return (
    <>
      <Navigation />
      <main className="shell stack">
        <section className="section-heading">
          <p className="eyebrow">New intake</p>
          <h1 className="page-title">Guide the agent through the required deal fields and generate the agreement in one flow.</h1>
        </section>
        <section className="split">
          <SubmitForm />
          <article className="card">
            <p className="eyebrow">Expected output</p>
            <h2>Structured, agent-friendly, delivery-ready.</h2>
            <ul className="plain-list">
              <li>AI-style guided intake for the contract fields that matter</li>
              <li>Template-aware agreement generation with structured preview data</li>
              <li>Simulated email and PDF download actions for proposal demos</li>
              <li>Broker review flag applied automatically when required</li>
            </ul>
          </article>
        </section>
      </main>
    </>
  );
}

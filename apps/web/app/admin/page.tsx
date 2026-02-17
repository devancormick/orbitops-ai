import { AdminWorkflowForm } from "../../components/admin-workflow-form";
import { Navigation } from "../../components/nav";

export default function AdminPage() {
  return (
    <>
      <Navigation />
      <main className="shell stack">
        <section className="section-heading">
          <p className="eyebrow">Admin controls</p>
          <h1 className="page-title">Manage workflow templates and shape how the routing system behaves.</h1>
        </section>
        <section className="split">
          <AdminWorkflowForm />
          <article className="card">
            <p className="eyebrow">Current admin scope</p>
            <h2>Workflow governance is built in.</h2>
            <ul className="plain-list">
              <li>Create active workflow templates by task type and workspace</li>
              <li>Set primary and fallback models per workflow</li>
              <li>Require review at the workflow policy level</li>
              <li>Use role-checked API mutations with session tokens</li>
            </ul>
          </article>
        </section>
      </main>
    </>
  );
}

import { AdminWorkflowForm } from "../../components/admin-workflow-form";
import { Navigation } from "../../components/nav";

export default function AdminPage() {
  return (
    <>
      <Navigation />
      <main className="shell stack">
        <section className="section-heading">
          <p className="eyebrow">Admin controls</p>
          <h1 className="page-title">Manage contract templates and keep the private demo easy to extend.</h1>
        </section>
        <section className="split">
          <AdminWorkflowForm />
          <article className="card">
            <p className="eyebrow">Current admin scope</p>
            <h2>Template governance is built in.</h2>
            <ul className="plain-list">
              <li>Create active agreement templates by workspace</li>
              <li>Define the intake structure agents will follow</li>
              <li>Require broker review at the template policy level</li>
              <li>Use role-checked API mutations with session tokens</li>
            </ul>
          </article>
        </section>
      </main>
    </>
  );
}

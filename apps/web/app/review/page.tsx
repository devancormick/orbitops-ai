import { Navigation } from "../../components/nav";
import { reviewQueue } from "../../lib/data";

export default function ReviewPage() {
  return (
    <>
      <Navigation />
      <main className="shell stack">
        <section className="section-heading">
          <p className="eyebrow">Approval queue</p>
          <h1 className="page-title">Human checkpoints stay embedded in the workflow instead of bolted on later.</h1>
        </section>
        <section className="split">
          <article className="card">
            <h2>Waiting for review</h2>
            <div className="table">
              {reviewQueue.map((item) => (
                <div key={item.id} className="table-row">
                  <div>
                    <strong>{item.id}</strong>
                    <p>{item.workflow}</p>
                  </div>
                  <div>
                    <strong>{item.priority}</strong>
                    <p>{item.reviewer}</p>
                  </div>
                  <div>
                    <strong>{item.age}</strong>
                    <p>Open</p>
                  </div>
                </div>
              ))}
            </div>
          </article>
          <article className="card">
            <p className="eyebrow">Selected item</p>
            <h2>Policy Delta Check</h2>
            <p>
              The output matched schema, but three indemnity clauses changed enough to require legal ops
              approval before publishing the structured result back to the workspace.
            </p>
            <div className="action-row">
              <button className="button button-primary" type="button">Approve result</button>
              <button className="button button-secondary" type="button">Request re-run</button>
            </div>
          </article>
        </section>
      </main>
    </>
  );
}

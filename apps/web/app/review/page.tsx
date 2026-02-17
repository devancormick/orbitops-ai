import { Navigation } from "../../components/nav";
import { getDashboardData } from "../../lib/api";

export default async function ReviewPage() {
  const dashboard = await getDashboardData();
  const selected = dashboard.review_queue[0];

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
              {dashboard.review_queue.map((item) => (
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
                    <p>{item.status}</p>
                  </div>
                </div>
              ))}
            </div>
          </article>
          <article className="card">
            <p className="eyebrow">Selected item</p>
            <h2>{selected?.workflow ?? "No reviews pending"}</h2>
            <p>
              {selected?.summary ??
                "When a workflow requires review, the selected run appears here with context for the approver."}
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

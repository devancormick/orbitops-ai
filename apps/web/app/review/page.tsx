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
          <p className="eyebrow">Review queue</p>
          <h1 className="page-title">Broker approval stays embedded in the contract flow instead of becoming a manual side process.</h1>
        </section>
        <section className="split">
          <article className="card">
            <h2>Waiting for review</h2>
            <div className="table">
              {dashboard.review_queue.map((item) => (
                <div key={item.id} className="table-row">
                  <div>
                    <strong>{item.id}</strong>
                    <p>{item.template_name}</p>
                  </div>
                  <div>
                    <strong>{item.priority}</strong>
                    <p>{item.reviewer}</p>
                  </div>
                  <div>
                    <strong>{item.status}</strong>
                    <p>{item.requested_by}</p>
                  </div>
                </div>
              ))}
            </div>
          </article>
          <article className="card">
            <p className="eyebrow">Selected item</p>
            <h2>{selected?.template_name ?? "No reviews pending"}</h2>
            <p>
              {selected?.summary ??
                "When a generated agreement requires review, the selected document appears here with the broker notes and approval context."}
            </p>
            <div className="action-row">
              <button className="button button-primary" type="button">Approve packet</button>
              <button className="button button-secondary" type="button">Request edits</button>
            </div>
          </article>
        </section>
      </main>
    </>
  );
}

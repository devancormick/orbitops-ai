import { Navigation } from "../../components/nav";
import { getDocuments } from "../../lib/api";

export default async function RunsPage() {
  const documents = await getDocuments();

  return (
    <>
      <Navigation />
      <main className="shell stack">
        <section className="section-heading">
          <p className="eyebrow">Generated documents</p>
          <h1 className="page-title">Every agreement stays visible with template, recipient, preview, and delivery state.</h1>
        </section>
        <section className="split">
          <article className="card">
            <h2>Recent agreements</h2>
            <div className="table">
              {documents.map((document) => (
                <div key={document.id} className="table-row">
                  <div>
                    <strong>{document.id}</strong>
                    <p>{document.template_name}</p>
                  </div>
                  <div>
                    <strong>{document.status}</strong>
                    <p>{document.recipient_email}</p>
                  </div>
                  <div>
                    <strong>{document.generated_at}</strong>
                    <p>{document.workspace}</p>
                  </div>
                </div>
              ))}
            </div>
          </article>
          <article className="card dark-card">
            <h2>Preview focus</h2>
            <div className="metric-stack">
              {documents.slice(0, 3).map((document) => (
                <div key={document.id} className="metric-row">
                  <div>
                    <strong>{document.preview_title}</strong>
                    <p>{document.summary}</p>
                  </div>
                  <div>
                    <strong>{document.email_status}</strong>
                    <p>{document.download_status}</p>
                  </div>
                </div>
              ))}
            </div>
          </article>
        </section>
      </main>
    </>
  );
}

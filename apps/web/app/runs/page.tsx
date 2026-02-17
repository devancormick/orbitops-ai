import { Navigation } from "../../components/nav";
import { providerHealth, runHistory } from "../../lib/data";

export default function RunsPage() {
  return (
    <>
      <Navigation />
      <main className="shell stack">
        <section className="section-heading">
          <p className="eyebrow">Run history</p>
          <h1 className="page-title">Every route, output, and fallback stays visible after execution.</h1>
        </section>
        <section className="split">
          <article className="card">
            <h2>Recent runs</h2>
            <div className="table">
              {runHistory.map((run) => (
                <div key={run.id} className="table-row">
                  <div>
                    <strong>{run.id}</strong>
                    <p>{run.workflow}</p>
                  </div>
                  <div>
                    <strong>{run.model}</strong>
                    <p>{run.provider}</p>
                  </div>
                  <div>
                    <strong>{run.outcome}</strong>
                    <p>{run.submittedAt}</p>
                  </div>
                </div>
              ))}
            </div>
          </article>
          <article className="card dark-card">
            <h2>Provider health</h2>
            <div className="metric-stack">
              {providerHealth.map((provider) => (
                <div key={provider.name} className="metric-row">
                  <div>
                    <strong>{provider.name}</strong>
                    <p>{provider.strength}</p>
                  </div>
                  <div>
                    <strong>{provider.status}</strong>
                    <p>{provider.latency}</p>
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

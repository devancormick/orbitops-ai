import { Navigation } from "../../components/nav";
import { getDashboardData } from "../../lib/api";

export default async function RunsPage() {
  const dashboard = await getDashboardData();
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
              {dashboard.runs.map((run) => (
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
                    <p>{run.submitted_at}</p>
                  </div>
                </div>
              ))}
            </div>
          </article>
          <article className="card dark-card">
            <h2>Provider health</h2>
            <div className="metric-stack">
              {dashboard.provider_health.map((provider) => (
                <div key={provider.provider} className="metric-row">
                  <div>
                    <strong>{provider.provider}</strong>
                    <p>{provider.strongest_for}</p>
                  </div>
                  <div>
                    <strong>{provider.status}</strong>
                    <p>{provider.median_latency}</p>
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

import { DailyAlertsChart } from "../components/DailyAlertsChart.js";
import { Panel } from "../components/Panel.js";
import { ReportFiltersBar } from "../components/ReportFiltersBar.js";
import { StatTile } from "../components/StatTile.js";
import { api } from "../lib/api.js";
import { useIdentity } from "../lib/identity.js";
import { useApiData } from "../lib/use-api-data.js";
import { useReportFilters } from "../lib/use-report-filters.js";

const EMPTY: readonly string[] = [];

/** CMV Traffic Alert report: one page, several panels, all driven by the same agency + range filters. */
export function CmvAlertsPage() {
  const { userId } = useIdentity();
  const me = useApiData(`me:${userId}`, (signal) => api.me(signal));
  const allowed = me.data?.agencies.map((agency) => agency.agency) ?? EMPTY;
  const [filters, setFilters] = useReportFilters(allowed);
  const { agency, range } = filters;

  const daily = useApiData(agency ? `daily-alerts:${userId}:${agency}:${range}` : null, (signal) =>
    api.cmvAlerts.dailyAlerts({ agency: agency as string, range }, signal),
  );

  if (me.error) return <p role="alert">Couldn't load your account: {me.error.message}</p>;
  if (!me.data) return <p>Loading…</p>;

  return (
    <div className="report">
      <header className="report__header">
        <h1>CMV Traffic Alerts</h1>
        <ReportFiltersBar agencies={me.data.agencies} filters={filters} onChange={setFilters} />
        {daily.data && <p className="report__as-of">Data as of {new Date(daily.data.data_as_of).toLocaleString()}</p>}
      </header>

      <div className="report__tiles">
        <StatTile label="Total alerts" value={daily.data?.total} />
      </div>

      <Panel
        title="Alerts per day"
        loading={daily.loading}
        error={daily.error}
        empty={daily.data?.per_day.length === 0}
      >
        {daily.data && <DailyAlertsChart days={daily.data.per_day} />}
      </Panel>
    </div>
  );
}

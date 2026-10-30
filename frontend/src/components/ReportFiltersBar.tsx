import { type AgencySummary, REPORT_RANGES, type ReportRange } from "../api/types.js";
import type { ReportFilters } from "../lib/use-report-filters.js";

const RANGE_LABELS: Record<ReportRange, string> = {
  "7d": "Last 7 days",
  "30d": "Last 30 days",
  "90d": "Last 90 days",
};

type Props = {
  agencies: readonly AgencySummary[];
  filters: ReportFilters;
  onChange: (next: Partial<ReportFilters>) => void;
};

/** Filters apply as soon as they change (no Apply button), the same as the Tableau dashboards. */
export function ReportFiltersBar({ agencies, filters, onChange }: Props) {
  return (
    <div className="filters">
      {agencies.length > 1 && (
        <label>
          Agency
          <select value={filters.agency ?? ""} onChange={(event) => onChange({ agency: event.target.value })}>
            {agencies.map((agency) => (
              <option key={agency.agency} value={agency.agency}>
                {agency.name}
              </option>
            ))}
          </select>
        </label>
      )}
      <label>
        Period
        <select value={filters.range} onChange={(event) => onChange({ range: event.target.value as ReportRange })}>
          {REPORT_RANGES.map((range) => (
            <option key={range} value={range}>
              {RANGE_LABELS[range]}
            </option>
          ))}
        </select>
      </label>
    </div>
  );
}

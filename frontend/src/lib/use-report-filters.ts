import { useCallback, useMemo } from "react";
import { useSearchParams } from "react-router";
import { DEFAULT_RANGE, REPORT_RANGES, type ReportRange } from "../api/types.js";

export type ReportFilters = {
  agency: string | undefined;
  range: ReportRange;
};

/**
 * Report filters live in the URL (`?agency=IN-DOT&range=30d`) so a view can be bookmarked or shared. Invalid values
 * fall back to defaults. Changes replace the current history entry instead of adding one, so Back leaves the report.
 */
export function useReportFilters(
  allowedAgencies: readonly string[],
): [ReportFilters, (next: Partial<ReportFilters>) => void] {
  const [params, setParams] = useSearchParams();

  const filters = useMemo<ReportFilters>(() => {
    const agencyParam = params.get("agency");
    const rangeParam = params.get("range");
    return {
      agency: agencyParam && allowedAgencies.includes(agencyParam) ? agencyParam : allowedAgencies[0],
      range: isReportRange(rangeParam) ? rangeParam : DEFAULT_RANGE,
    };
  }, [params, allowedAgencies]);

  const setFilters = useCallback(
    (next: Partial<ReportFilters>) => {
      setParams(
        (current) => {
          const updated = new URLSearchParams(current);
          for (const [key, value] of Object.entries(next)) {
            if (value === undefined) updated.delete(key);
            else updated.set(key, value);
          }
          return updated;
        },
        { replace: true },
      );
    },
    [setParams],
  );

  return [filters, setFilters];
}

function isReportRange(value: string | null): value is ReportRange {
  return REPORT_RANGES.includes(value as ReportRange);
}

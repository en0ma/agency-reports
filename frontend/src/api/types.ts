/**
 * Friendly names for the API types. Everything here comes from schema.d.ts, which is generated from the Django
 * serializers (`npm run gen:api`), so the frontend and backend can't drift apart without `npm run check` failing.
 */
import type { components, operations } from "./schema.js";

type Schemas = components["schemas"];

export type ReportRange = Schemas["RangeEnum"];
export type AgencySummary = Schemas["AgencySummary"];
export type MeResponse = Schemas["MeResponse"];
export type DailyAlertCount = Schemas["DailyAlertCount"];
export type DailyAlertsResponse = Schemas["DailyAlertsResponse"];

export type CmvAlertsQuery = NonNullable<operations["cmv_alerts_daily_alerts_retrieve"]["parameters"]["query"]>;

/** Body of every non-2xx API response (core/errors.py). */
export type ApiErrorBody = {
  status_code: number;
  error: string;
  message: string;
};

/** Reporting periods every report supports, in display order. Must list every value of ReportRange. */
export const REPORT_RANGES = ["7d", "30d", "90d"] as const satisfies readonly ReportRange[];
export const DEFAULT_RANGE: ReportRange = "30d";

// Fails to compile if the backend adds a range this list doesn't have.
type _AllRangesListed = ReportRange extends (typeof REPORT_RANGES)[number] ? true : never;
export const _allRangesListed: _AllRangesListed = true;

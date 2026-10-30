import type { CmvAlertsQuery, DailyAlertsResponse, MeResponse } from "../api/types.js";
import { apiGet } from "./api-client.js";

/** Typed API functions, one per endpoint. Request and response types are generated from the backend (see api/types.ts). */
export const api = {
  me: (signal?: AbortSignal) => apiGet<MeResponse>("/me", {}, signal),

  cmvAlerts: {
    dailyAlerts: (query: CmvAlertsQuery, signal?: AbortSignal) =>
      apiGet<DailyAlertsResponse>("/cmv-alerts/daily-alerts", query, signal),
  },
};

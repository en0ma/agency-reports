import { render, screen, within } from "@testing-library/react";
import { MemoryRouter } from "react-router";
import { describe, expect, it, vi } from "vitest";
import type { DailyAlertsResponse, MeResponse } from "../src/api/types.js";
import { IdentityProvider } from "../src/lib/identity.js";
import { CmvAlertsPage } from "../src/pages/CmvAlertsPage.js";

const me: MeResponse = {
  user_id: "support.staff",
  display_name: "Support",
  internal: true,
  agencies: [
    { agency: "IA-DOT", name: "Iowa DOT" },
    { agency: "IN-DOT", name: "Indiana DOT" },
  ],
};

const daily = (agency: string, range: string, perDay: DailyAlertsResponse["per_day"]): DailyAlertsResponse => ({
  agency,
  range: range as DailyAlertsResponse["range"],
  data_as_of: "2026-11-08T06:00:00Z",
  generated_at: "2026-11-08T07:00:00Z",
  total: perDay.reduce((sum, day) => sum + day.alerts, 0),
  per_day: perDay,
});

/** Routes fetch calls by path, and records the URLs requested. */
function stubApi(dailyFor: (params: URLSearchParams) => DailyAlertsResponse) {
  const urls: string[] = [];
  vi.stubGlobal("fetch", async (input: string) => {
    urls.push(input);
    const url = new URL(input, "http://localhost");
    if (url.pathname === "/api/me") return Response.json(me);
    if (url.pathname === "/api/cmv-alerts/daily-alerts") return Response.json(dailyFor(url.searchParams));
    return Response.json({ status_code: 404, error: "Not Found", message: "nope" }, { status: 404 });
  });
  return urls;
}

function renderAt(path: string) {
  return render(
    <MemoryRouter initialEntries={[path]}>
      <IdentityProvider>
        <CmvAlertsPage />
      </IdentityProvider>
    </MemoryRouter>,
  );
}

describe("CmvAlertsPage", () => {
  it("loads the agency and range from the URL", async () => {
    const urls = stubApi((params) =>
      daily(params.get("agency") ?? "", params.get("range") ?? "", [
        { day: "2026-11-06", alerts: 40 },
        { day: "2026-11-07", alerts: 2 },
      ]),
    );

    renderAt("/cmv-alerts?agency=IN-DOT&range=7d");

    const tile = await screen.findByText("42");
    expect(tile).toBeInTheDocument();
    expect(urls).toContain("/api/cmv-alerts/daily-alerts?agency=IN-DOT&range=7d");
  });

  it("falls back to the first allowed agency and the default range for invalid URL values", async () => {
    const urls = stubApi((params) => daily(params.get("agency") ?? "", params.get("range") ?? "", []));

    renderAt("/cmv-alerts?agency=OH-DOT&range=forever");

    await screen.findByText("No alerts in this period.");
    expect(urls).toContain("/api/cmv-alerts/daily-alerts?agency=IA-DOT&range=30d");
  });

  it("shows the panel's error without breaking the page", async () => {
    vi.stubGlobal("fetch", async (input: string) =>
      input === "/api/me"
        ? Response.json(me)
        : Response.json({ status_code: 500, error: "Internal", message: "warehouse unavailable" }, { status: 500 }),
    );

    renderAt("/cmv-alerts");

    const panel = await screen.findByRole("region", { name: "Alerts per day" });
    expect(await within(panel).findByRole("alert")).toHaveTextContent("warehouse unavailable");
    expect(screen.getByRole("heading", { name: "CMV Traffic Alerts" })).toBeInTheDocument();
  });
});

import { describe, expect, it, vi } from "vitest";
import { ApiError, apiGet, buildUrl } from "../src/lib/api-client.js";

describe("buildUrl", () => {
  it("prefixes /api and drops undefined params", () => {
    expect(buildUrl("/cmv-alerts/daily-alerts", { agency: "IN-DOT", range: undefined })).toBe(
      "/api/cmv-alerts/daily-alerts?agency=IN-DOT",
    );
  });

  it("omits the query string when there are no params", () => {
    expect(buildUrl("/me", {})).toBe("/api/me");
  });
});

describe("apiGet", () => {
  it("sends the demo user header and returns the parsed body", async () => {
    const fetchMock = vi.fn(async () => Response.json({ ok: true }));
    vi.stubGlobal("fetch", fetchMock);

    await expect(apiGet("/me")).resolves.toEqual({ ok: true });

    const [, init] = fetchMock.mock.calls[0] as unknown as [string, RequestInit];
    expect((init.headers as Record<string, string>)["X-Demo-User"]).toBeTruthy();
  });

  it("turns an error response into an ApiError with the server's message", async () => {
    vi.stubGlobal("fetch", async () =>
      Response.json({ status_code: 403, error: "Forbidden", message: "No access" }, { status: 403 }),
    );

    const error = await apiGet("/me").catch((e: unknown) => e);

    expect(error).toBeInstanceOf(ApiError);
    expect(error).toMatchObject({ status: 403, message: "No access" });
  });
});

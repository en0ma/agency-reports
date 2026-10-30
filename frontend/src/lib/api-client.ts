import type { ApiErrorBody } from "../api/types.js";
import { getCurrentUserId } from "./identity.js";

export class ApiError extends Error {
  override name = "ApiError";

  constructor(
    readonly status: number,
    message: string,
  ) {
    super(message);
  }
}

export type QueryValue = string | number | undefined;

/**
 * The only place the frontend calls fetch. Builds the URL from named params (dropping undefined ones), attaches the
 * caller's identity, and turns non-2xx responses into ApiError. Components use the typed functions in `api.ts`.
 */
export async function apiGet<T>(
  path: string,
  params: Record<string, QueryValue> = {},
  signal?: AbortSignal,
): Promise<T> {
  const response = await fetch(buildUrl(path, params), {
    headers: { Accept: "application/json", "X-Demo-User": getCurrentUserId() },
    signal,
  });

  if (!response.ok) {
    const body = (await response.json().catch(() => null)) as Partial<ApiErrorBody> | null;
    throw new ApiError(response.status, body?.message ?? response.statusText);
  }
  return (await response.json()) as T;
}

export function buildUrl(path: string, params: Record<string, QueryValue>): string {
  const search = new URLSearchParams();
  for (const [key, value] of Object.entries(params)) {
    if (value !== undefined) search.set(key, String(value));
  }
  const query = search.toString();
  return query ? `/api${path}?${query}` : `/api${path}`;
}

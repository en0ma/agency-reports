import { useEffect, useState } from "react";

const CACHE_TTL_MS = 5 * 60 * 1000;
const cache = new Map<string, { data: unknown; storedAt: number }>();

export type ApiData<T> = {
  data: T | undefined;
  error: Error | undefined;
  /** True while a request is in flight. `data` keeps the previous result meanwhile, so panels don't flash empty. */
  loading: boolean;
};

/**
 * Loads data for a panel. `key` identifies the request (include every input, e.g. user + agency + range); when it
 * changes the in-flight request is aborted, so an older response can never replace a newer one. Results are cached
 * for 5 minutes per key. Pass `key = null` to skip loading (e.g. until an agency is chosen).
 */
export function useApiData<T>(key: string | null, load: (signal: AbortSignal) => Promise<T>): ApiData<T> {
  const [state, setState] = useState<ApiData<T>>({ data: undefined, error: undefined, loading: key !== null });

  // `load` is usually an inline arrow; `key` captures everything it depends on.
  // biome-ignore lint/correctness/useExhaustiveDependencies: key captures load's inputs
  useEffect(() => {
    if (key === null) return;

    const cached = cache.get(key);
    if (cached && Date.now() - cached.storedAt < CACHE_TTL_MS) {
      setState({ data: cached.data as T, error: undefined, loading: false });
      return;
    }

    const controller = new AbortController();
    setState((previous) => ({ ...previous, error: undefined, loading: true }));

    load(controller.signal).then(
      (data) => {
        cache.set(key, { data, storedAt: Date.now() });
        setState({ data, error: undefined, loading: false });
      },
      (error: unknown) => {
        if (controller.signal.aborted) return;
        setState((previous) => ({ ...previous, error: error as Error, loading: false }));
      },
    );

    return () => controller.abort();
  }, [key]);

  return state;
}

/** For tests. */
export function clearApiDataCache(): void {
  cache.clear();
}

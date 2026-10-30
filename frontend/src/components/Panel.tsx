import type { ReactNode } from "react";

type PanelProps = {
  title: string;
  loading: boolean;
  error: Error | undefined;
  /** Shown instead of children when the panel has loaded but there's nothing to show. */
  empty?: boolean;
  children: ReactNode;
};

/** Card that every report panel renders inside. Handles loading, error and empty states the same way everywhere. */
export function Panel({ title, loading, error, empty = false, children }: PanelProps) {
  return (
    <section className="panel" aria-busy={loading} aria-label={title}>
      <header className="panel__header">
        <h2>{title}</h2>
        {loading && <span className="panel__loading">Loading…</span>}
      </header>
      {error ? (
        <p className="panel__error" role="alert">
          Couldn't load this panel: {error.message}
        </p>
      ) : empty && !loading ? (
        <p className="panel__empty">No alerts in this period.</p>
      ) : (
        children
      )}
    </section>
  );
}

export function StatTile({ label, value }: { label: string; value: number | undefined }) {
  return (
    <div className="stat-tile">
      <span className="stat-tile__label">{label}</span>
      <span className="stat-tile__value">{value === undefined ? "–" : value.toLocaleString()}</span>
    </div>
  );
}

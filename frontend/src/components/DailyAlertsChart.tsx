import type { DailyAlertCount } from "../api/types.js";

const HEIGHT = 160;
const BAR_GAP = 2;

/**
 * Bar chart of alerts per day. Plain SVG for now; the charting library decision (MUI X Charts / Recharts / ECharts)
 * is still open, and this component is the only thing that changes when it's made.
 */
export function DailyAlertsChart({ days }: { days: readonly DailyAlertCount[] }) {
  const max = Math.max(1, ...days.map((day) => day.alerts));
  const barWidth = 12;
  const width = days.length * (barWidth + BAR_GAP);

  return (
    <svg
      className="daily-chart"
      viewBox={`0 0 ${Math.max(width, 1)} ${HEIGHT}`}
      preserveAspectRatio="none"
      role="img"
      aria-label={`Alerts per day, ${days.length} days`}
    >
      {days.map((day, index) => {
        const barHeight = (day.alerts / max) * (HEIGHT - 4);
        return (
          <rect
            key={day.day}
            x={index * (barWidth + BAR_GAP)}
            y={HEIGHT - barHeight}
            width={barWidth}
            height={barHeight}
            rx={2}
          >
            <title>{`${day.day}: ${day.alerts.toLocaleString()} alerts`}</title>
          </rect>
        );
      })}
    </svg>
  );
}

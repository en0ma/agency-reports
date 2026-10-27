"""Read-only queries for the CMV Traffic Alert report, one function per panel.

All aggregation happens in the warehouse: return the small, already-aggregated result a panel needs, never raw alert
rows.
"""

import logging
import time
from dataclasses import dataclass

from django.db.models import Count
from django.db.models.functions import Substr

from warehouse.models import CmvAlert

log = logging.getLogger("agency_reports.warehouse")


@dataclass(frozen=True)
class AlertWindow:
    agency: str
    start: str  # inclusive ISO-8601 UTC
    end: str  # exclusive ISO-8601 UTC


def _alerts_in(window: AlertWindow):
    """Real alerts for one agency in the window. Field-tech test alerts (is_test) never count, the same as Tableau."""
    return CmvAlert.objects.filter(
        agency_id=window.agency,
        is_test=False,
        alert_ts_utc__gte=window.start,
        alert_ts_utc__lt=window.end,
    )


def daily_alerts(window: AlertWindow) -> list[dict]:
    started = time.perf_counter()
    rows = list(
        _alerts_in(window)
        .annotate(day=Substr("alert_ts_utc", 1, 10))
        .values("day")
        .annotate(alerts=Count("alert_id"))
        .order_by("day")
    )
    _log_query("daily_alerts", window, rows, started)
    return rows


def _log_query(name: str, window: AlertWindow, rows: list, started: float) -> None:
    log.info(
        "warehouse query",
        extra={
            "query": name,
            "rows": len(rows),
            "duration_ms": round((time.perf_counter() - started) * 1000),
            "params": {"agency": window.agency, "from": window.start, "to": window.end},
        },
    )

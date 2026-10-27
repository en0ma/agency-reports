from datetime import datetime, timedelta

REPORT_RANGES = ("7d", "30d", "90d")
DEFAULT_RANGE = "30d"

_RANGE_DAYS = {"7d": 7, "30d": 30, "90d": 90}


def resolve_range(report_range: str, data_as_of: str) -> tuple[str, str]:
    """Turns a report range into a UTC window `(from, to)` that ends at the data's `data_as_of`, not "now", so a
    report never shows an empty tail for hours the ETL hasn't loaded yet. `from` is inclusive, `to` is exclusive.
    """
    try:
        to = datetime.fromisoformat(data_as_of.replace("Z", "+00:00"))
    except ValueError as error:
        raise ValueError(f"Invalid data_as_of: {data_as_of}") from error
    start = to - timedelta(days=_RANGE_DAYS[report_range])
    return _warehouse_timestamp(start), _warehouse_timestamp(to)


def _warehouse_timestamp(moment: datetime) -> str:
    """The warehouse stores timestamps as `YYYY-MM-DDTHH:MM:SSZ`, so compare in that exact format."""
    return moment.strftime("%Y-%m-%dT%H:%M:%SZ")

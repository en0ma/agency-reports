import pytest

from core.ranges import resolve_range


@pytest.mark.parametrize(
    ("report_range", "start"),
    [("7d", "2026-11-01T06:00:00Z"), ("30d", "2026-10-09T06:00:00Z"), ("90d", "2026-08-10T06:00:00Z")],
)
def test_window_ends_at_data_as_of(report_range, start):
    assert resolve_range(report_range, "2026-11-08T06:00:00Z") == (start, "2026-11-08T06:00:00Z")


def test_returns_the_warehouse_timestamp_format():
    assert resolve_range("7d", "2026-11-08T06:00:00.000Z") == ("2026-11-01T06:00:00Z", "2026-11-08T06:00:00Z")


def test_rejects_an_unparseable_data_as_of():
    with pytest.raises(ValueError, match="Invalid data_as_of"):
        resolve_range("7d", "yesterday")

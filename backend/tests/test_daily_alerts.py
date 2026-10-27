from datetime import datetime

import pytest

URL = "/api/cmv-alerts/daily-alerts"


def test_returns_per_day_counts_total_and_freshness(api):
    response = api.as_user("indiana.analyst").get(URL, {"agency": "IN-DOT", "range": "7d"})

    assert response.status_code == 200
    body = response.json()
    assert body["agency"] == "IN-DOT"
    assert body["range"] == "7d"
    assert body["data_as_of"] == "2026-11-01T06:00:00Z"
    assert datetime.fromisoformat(body["generated_at"])
    assert body["per_day"] == [
        {"day": "2026-10-29", "alerts": 1},
        {"day": "2026-10-30", "alerts": 3},
        {"day": "2026-10-31", "alerts": 1},
        {"day": "2026-11-01", "alerts": 1},
    ]
    assert body["total"] == 6


def test_excludes_field_tech_test_alerts(api):
    body = api.as_user("indiana.analyst").get(URL, {"agency": "IN-DOT", "range": "7d"}).json()

    # a05 and a07 are is_test alerts on 10-30 and 10-31.
    assert {"day": "2026-10-30", "alerts": 3} in body["per_day"]
    assert {"day": "2026-10-31", "alerts": 1} in body["per_day"]


def test_window_ends_at_data_as_of(api):
    body = api.as_user("indiana.analyst").get(URL, {"agency": "IN-DOT", "range": "7d"}).json()

    # a08 (05:59:59Z) is inside the window; a09 (exactly at data_as_of) is not.
    assert body["per_day"][-1] == {"day": "2026-11-01", "alerts": 1}


def test_defaults_to_30_days(api):
    assert api.as_user("indiana.analyst").get(URL, {"agency": "IN-DOT"}).json()["range"] == "30d"


def test_returns_an_empty_series_when_there_is_no_data(api):
    from warehouse.models import CmvAlert

    CmvAlert.objects.filter(agency_id="IN-DOT").delete()

    body = api.as_user("indiana.analyst").get(URL, {"agency": "IN-DOT"}).json()

    assert body["total"] == 0
    assert body["per_day"] == []


class TestAgencyIsolation:
    def test_403_and_no_query_for_an_agency_the_user_may_not_see(self, api, django_assert_num_queries):
        client = api.as_user("indiana.analyst")
        with django_assert_num_queries(0):
            response = client.get(URL, {"agency": "IA-DOT"})

        assert response.status_code == 403

    def test_internal_user_can_read_any_allowed_agency(self, api):
        response = api.as_user("support.staff").get(URL, {"agency": "IA-DOT"})

        assert response.status_code == 200
        assert response.json()["total"] == 2

    def test_403_for_a_well_formed_agency_nobody_has(self, api):
        assert api.as_user("support.staff").get(URL, {"agency": "ZZ-DOT"}).status_code == 403


class TestValidation:
    @pytest.mark.parametrize(
        "params",
        [{"range": "7d"}, {"agency": "in-dot"}, {"agency": "IN-DOT", "range": "1y"}, {"agency": "IN-DOT", "foo": "1"}],
        ids=["missing agency", "malformed agency", "unknown range", "unknown parameter"],
    )
    def test_400_and_no_query(self, api, django_assert_num_queries, params):
        client = api.as_user("indiana.analyst")
        with django_assert_num_queries(0):
            response = client.get(URL, params)

        assert response.status_code == 400
        assert set(response.json()) == {"status_code", "error", "message"}

    def test_401_before_validation_when_there_is_no_identity(self, api):
        assert api.get(URL, {"agency": "nope"}).status_code == 401

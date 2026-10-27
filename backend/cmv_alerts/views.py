from django.utils import timezone
from drf_spectacular.utils import extend_schema
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from core.identity import assert_agency_access
from core.ranges import resolve_range
from warehouse.models import data_as_of

from . import queries
from .serializers import CmvAlertsQuerySerializer, DailyAlertsResponseSerializer


def _report_window(request: Request) -> tuple[dict, queries.AlertWindow]:
    """Validates the query string, enforces agency isolation, and resolves the range against the data's freshness.

    Every panel starts with this, in this order: nothing is queried until the agency check has passed.
    """
    query = CmvAlertsQuerySerializer(data=request.query_params.dict())
    query.is_valid(raise_exception=True)
    agency, report_range = query.validated_data["agency"], query.validated_data["range"]

    assert_agency_access(request, agency)

    as_of = data_as_of("cmv_alerts")
    start, end = resolve_range(report_range, as_of)
    meta = {"agency": agency, "range": report_range, "data_as_of": as_of, "generated_at": timezone.now()}
    return meta, queries.AlertWindow(agency=agency, start=start, end=end)


class DailyAlertsView(APIView):
    """Daily alert totals for one agency over the selected range. Panel: "Alerts per day"."""

    @extend_schema(parameters=[CmvAlertsQuerySerializer], responses=DailyAlertsResponseSerializer, tags=["cmv-alerts"])
    def get(self, request: Request) -> Response:
        meta, window = _report_window(request)
        per_day = queries.daily_alerts(window)
        payload = {**meta, "total": sum(day["alerts"] for day in per_day), "per_day": per_day}
        return Response(DailyAlertsResponseSerializer(payload).data)

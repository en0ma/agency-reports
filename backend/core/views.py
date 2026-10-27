from drf_spectacular.utils import extend_schema
from rest_framework import serializers
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from warehouse.models import Agency


class HealthResponseSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=["ok"])


class HealthView(APIView):
    authentication_classes = ()
    permission_classes = ()

    @extend_schema(responses=HealthResponseSerializer, auth=[])
    def get(self, request: Request) -> Response:
        return Response({"status": "ok"})


class AgencySummarySerializer(serializers.Serializer):
    agency = serializers.CharField()
    name = serializers.CharField()


class MeResponseSerializer(serializers.Serializer):
    user_id = serializers.CharField()
    display_name = serializers.CharField()
    internal = serializers.BooleanField()
    agencies = AgencySummarySerializer(many=True)


class MeView(APIView):
    """Who the caller is and which agencies they may pick in the UI."""

    @extend_schema(responses=MeResponseSerializer)
    def get(self, request: Request) -> Response:
        user = request.user
        agencies = Agency.objects.filter(agency__in=user.allowed_agencies).order_by("agency").values("agency", "name")
        return Response(
            MeResponseSerializer(
                {
                    "user_id": user.user_id,
                    "display_name": user.display_name,
                    "internal": user.internal,
                    "agencies": list(agencies),
                }
            ).data
        )

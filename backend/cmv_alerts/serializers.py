from rest_framework import serializers

from core.ranges import DEFAULT_RANGE, REPORT_RANGES

AGENCY_CODE_PATTERN = r"^[A-Z]{2}-DOT$"


class CmvAlertsQuerySerializer(serializers.Serializer):
    """Query string shared by every CMV Traffic Alert panel. Unknown parameters are rejected."""

    agency = serializers.RegexField(AGENCY_CODE_PATTERN, help_text="Agency code, e.g. IN-DOT")
    range = serializers.ChoiceField(choices=REPORT_RANGES, default=DEFAULT_RANGE, required=False)

    def to_internal_value(self, data):
        unknown = set(data) - set(self.fields)
        if unknown:
            raise serializers.ValidationError({name: "Unknown parameter" for name in sorted(unknown)})
        return super().to_internal_value(data)


class ReportMetaSerializer(serializers.Serializer):
    """Fields every report response carries, so the UI can show how fresh the data is."""

    agency = serializers.CharField()
    range = serializers.ChoiceField(choices=REPORT_RANGES)
    data_as_of = serializers.CharField(help_text="ISO timestamp of the last ETL run that wrote the data")
    generated_at = serializers.DateTimeField(help_text="When the backend built this response")


class DailyAlertCountSerializer(serializers.Serializer):
    day = serializers.CharField(help_text="Calendar day, YYYY-MM-DD")
    alerts = serializers.IntegerField()


class DailyAlertsResponseSerializer(ReportMetaSerializer):
    """GET /api/cmv-alerts/daily-alerts"""

    total = serializers.IntegerField()
    per_day = DailyAlertCountSerializer(many=True)

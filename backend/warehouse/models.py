"""Read-only models over the Smart Roadways gold tables (catalog `smart_roadways`, schema `gold` in Unity Catalog).

The ETL writes these tables; the portal never does, so every model is unmanaged (no migrations). Timestamps are stored
as ISO-8601 UTC text, e.g. '2026-11-02T23:41:07Z', exactly as the gold tables expose them. Column docs are in
data/warehouse/schema.sql.
"""

from django.db import models


class Agency(models.Model):
    agency = models.CharField(primary_key=True, max_length=16)  # e.g. 'IN-DOT'
    name = models.TextField()
    time_zone = models.TextField()  # IANA zone the agency reports in, e.g. 'America/Chicago'

    class Meta:
        managed = False
        db_table = "agencies"

    def __str__(self) -> str:
        return self.agency


class RoadSegment(models.Model):
    segment_id = models.CharField(primary_key=True, max_length=32)
    agency = models.ForeignKey(Agency, on_delete=models.DO_NOTHING, db_column="agency", related_name="segments")
    route = models.TextField()
    direction = models.TextField()
    segment_name = models.TextField(null=True)  # noqa: DJ001 (mirrors the gold table, which allows NULL)
    start_mm = models.FloatField()
    end_mm = models.FloatField()
    added_at = models.TextField()

    class Meta:
        managed = False
        db_table = "road_segments"

    def __str__(self) -> str:
        return self.segment_id


class CmvAlert(models.Model):
    alert_id = models.CharField(primary_key=True, max_length=32)
    agency = models.ForeignKey(Agency, on_delete=models.DO_NOTHING, db_column="agency", related_name="+")
    segment = models.ForeignKey(RoadSegment, on_delete=models.DO_NOTHING, db_column="segment_id", related_name="alerts")
    alert_ts_utc = models.TextField()
    alert_type = models.TextField()
    vehicle_id = models.TextField()
    is_test = models.BooleanField()

    class Meta:
        managed = False
        db_table = "cmv_alerts"

    def __str__(self) -> str:
        return self.alert_id


class TableMetadata(models.Model):
    # The gold table has no key; (table_name, data_as_of) is unique in practice.
    table_name = models.TextField(primary_key=True)
    data_as_of = models.TextField()

    class Meta:
        managed = False
        db_table = "table_metadata"

    def __str__(self) -> str:
        return f"{self.table_name}@{self.data_as_of}"


def data_as_of(table: str) -> str:
    """ISO timestamp of the latest ETL write to `table`."""
    latest = (
        TableMetadata.objects.filter(table_name=table)
        .order_by("-data_as_of")
        .values_list("data_as_of", flat=True)
        .first()
    )
    if latest is None:
        raise LookupError(f"No data_as_of recorded for table {table}")
    return latest

-- Local stand-in for the Smart Roadways gold tables in Unity Catalog (catalog `smart_roadways`, schema `gold`).
-- In production these live in Databricks and are written nightly by the Smart Roadways ETL; the portal only reads
-- them. Locally, each table is loaded from the CSV part files in data/warehouse/<table>/ into an in-memory SQLite
-- database, so the SQL here stays close to what runs on the Databricks SQL warehouse.
--
-- The CSVs are a synthetic sample. No real agency, vehicle or carrier data.

CREATE TABLE agencies (
  agency     TEXT PRIMARY KEY,  -- e.g. 'IN-DOT'
  name       TEXT NOT NULL,
  time_zone  TEXT NOT NULL      -- IANA zone the agency reports in, e.g. 'America/Chicago'
);

-- One row per instrumented road segment (a stretch of highway covered by roadside units).
CREATE TABLE road_segments (
  segment_id    TEXT PRIMARY KEY,
  agency        TEXT NOT NULL REFERENCES agencies (agency),
  route         TEXT NOT NULL,  -- e.g. 'I-65'
  direction     TEXT NOT NULL,  -- NB / SB / EB / WB
  segment_name  TEXT,           -- display name, assigned by the GIS team
  start_mm      REAL NOT NULL,  -- mile markers
  end_mm        REAL NOT NULL,
  added_at      TEXT NOT NULL   -- ISO-8601 UTC
);

-- One row per alert sent to a commercial motor vehicle (CMV) approaching a segment.
CREATE TABLE cmv_alerts (
  alert_id      TEXT PRIMARY KEY,
  agency        TEXT NOT NULL REFERENCES agencies (agency),
  segment_id    TEXT NOT NULL REFERENCES road_segments (segment_id),
  alert_ts_utc  TEXT NOT NULL,  -- ISO-8601 UTC, e.g. '2026-11-02T23:41:07Z'
  alert_type    TEXT NOT NULL,  -- slowdown_ahead / queue_warning / work_zone / hard_braking
  vehicle_id    TEXT NOT NULL,  -- pseudonymous vehicle key; never shown to agencies
  is_test       INTEGER NOT NULL DEFAULT 0  -- 1 = sent by field techs testing equipment
);

CREATE INDEX idx_cmv_alerts_agency_ts ON cmv_alerts (agency, alert_ts_utc);

-- When each table was last written by the ETL.
CREATE TABLE table_metadata (
  table_name  TEXT NOT NULL,
  data_as_of  TEXT NOT NULL  -- ISO-8601 UTC
);

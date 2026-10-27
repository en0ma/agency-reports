from pathlib import Path

import pytest
from django.db import connection
from rest_framework.test import APIClient

from warehouse.loader import load_warehouse

FIXTURE_DIR = Path(__file__).parent / "fixtures" / "warehouse"
SCHEMA_FILE = Path(__file__).resolve().parents[2] / "data" / "warehouse" / "schema.sql"


@pytest.fixture(scope="session")
def django_db_setup(django_db_setup, django_db_blocker):
    """Loads the small fixture CSVs in tests/fixtures/warehouse into the test database, using the real schema.

    Tests run the real queries against this data, so they catch query mistakes. Each test runs in a transaction that
    is rolled back, so a test can add rows of its own without affecting others.
    """
    with django_db_blocker.unblock():
        load_warehouse(connection, FIXTURE_DIR, schema_file=SCHEMA_FILE)


@pytest.fixture
def api(db):
    """An API client. Call `api.as_user("iowa.analyst")` to send requests as a demo user."""
    client = APIClient()

    def as_user(user_id: str) -> APIClient:
        client.credentials(HTTP_X_DEMO_USER=user_id)
        return client

    client.as_user = as_user
    return client

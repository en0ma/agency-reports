import pytest
from django.core.exceptions import ImproperlyConfigured

from agency_reports.env import load_env


def test_applies_defaults_when_only_app_env_is_set():
    env = load_env({"APP_ENV": "local"})

    assert env.app_env == "local"
    assert env.log_level == "INFO"
    assert env.warehouse_db_path.name == "warehouse.sqlite3"
    assert env.is_local


def test_lists_every_problem_at_once():
    with pytest.raises(ImproperlyConfigured) as error:
        load_env({"LOG_LEVEL": "loud"})

    message = str(error.value)
    assert "APP_ENV" in message
    assert "LOG_LEVEL" in message


def test_requires_secrets_outside_local():
    with pytest.raises(ImproperlyConfigured) as error:
        load_env({"APP_ENV": "prod"})

    message = str(error.value)
    assert "DJANGO_SECRET_KEY" in message
    assert "DATABRICKS_TOKEN" in message

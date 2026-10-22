"""Reads and validates the backend configuration from environment variables (and backend/.env, if present).

Every problem is collected and reported at once, so the app stops before it serves any traffic instead of failing on
the first request that touches a bad value.
"""

import os
from dataclasses import dataclass
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured
from dotenv import load_dotenv

BACKEND_DIR = Path(__file__).resolve().parent.parent

APP_ENVS = ("local", "dev", "devqa", "test", "prod")
LOG_LEVELS = ("CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG")


@dataclass(frozen=True)
class Env:
    app_env: str
    log_level: str
    secret_key: str
    warehouse_db_path: Path
    warehouse_data_dir: Path
    databricks_host: str
    databricks_token: str

    @property
    def is_local(self) -> bool:
        return self.app_env == "local"


def load_env(environ: dict[str, str] | None = None) -> Env:
    if environ is None:
        load_dotenv(BACKEND_DIR / ".env")
        environ = dict(os.environ)

    problems: list[str] = []

    # Required with no default, so a deployment that forgets to set it fails at startup instead of running with a
    # guessed environment.
    app_env = environ.get("APP_ENV", "")
    if app_env not in APP_ENVS:
        problems.append(f"APP_ENV: must be one of {', '.join(APP_ENVS)} (got {app_env!r})")

    log_level = environ.get("LOG_LEVEL", "INFO").upper()
    if log_level not in LOG_LEVELS:
        problems.append(f"LOG_LEVEL: must be one of {', '.join(LOG_LEVELS)} (got {log_level!r})")

    secret_key = environ.get("DJANGO_SECRET_KEY", "")
    if not secret_key:
        if app_env == "local":
            secret_key = "local-only-not-secret"
        else:
            problems.append("DJANGO_SECRET_KEY: required outside APP_ENV=local")

    databricks_host = environ.get("DATABRICKS_HOST", "")
    databricks_token = environ.get("DATABRICKS_TOKEN", "")
    if app_env not in ("", "local"):
        if not databricks_host:
            problems.append("DATABRICKS_HOST: required outside APP_ENV=local")
        if not databricks_token:
            problems.append("DATABRICKS_TOKEN: required outside APP_ENV=local")

    if problems:
        raise ImproperlyConfigured("Invalid backend configuration:\n" + "\n".join(f"  - {p}" for p in problems))

    return Env(
        app_env=app_env,
        log_level=log_level,
        secret_key=secret_key,
        warehouse_db_path=_resolve(environ.get("WAREHOUSE_DB_PATH", "../data/warehouse.sqlite3")),
        warehouse_data_dir=_resolve(environ.get("WAREHOUSE_DATA_DIR", "../data/warehouse")),
        databricks_host=databricks_host,
        databricks_token=databricks_token,
    )


def _resolve(path: str) -> Path:
    """Relative paths are relative to backend/, wherever the process was started from."""
    candidate = Path(path)
    return candidate if candidate.is_absolute() else (BACKEND_DIR / candidate).resolve()

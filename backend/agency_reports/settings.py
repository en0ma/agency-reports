from agency_reports.env import load_env

ENV = load_env()

SECRET_KEY = ENV.secret_key
DEBUG = ENV.is_local
ALLOWED_HOSTS = ["*"] if ENV.is_local else []

# No auth, admin or sessions apps: identity comes from the stand-in header for now (see core/identity.py), and the
# portal has no database of its own yet. Everything it reads lives in the warehouse.
INSTALLED_APPS = [
    "rest_framework",
    "drf_spectacular",
    "core",
    "warehouse",
    "cmv_alerts",
]

MIDDLEWARE = [
    "core.middleware.RequestLogMiddleware",
    "django.middleware.common.CommonMiddleware",
]

ROOT_URLCONF = "agency_reports.urls"
WSGI_APPLICATION = "agency_reports.wsgi.application"

# The warehouse. Locally a SQLite file built from data/warehouse/*.csv by `python manage.py load_warehouse`; in
# deployed environments the Databricks SQL warehouse (connection not wired up yet). Read-only from the portal's side:
# every model in warehouse/models.py is unmanaged.
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ENV.warehouse_db_path,
    }
}

WAREHOUSE_DATA_DIR = ENV.warehouse_data_dir

USE_TZ = True
TIME_ZONE = "UTC"
APPEND_SLASH = False
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": ["core.identity.StandInAuthentication"],
    "DEFAULT_PERMISSION_CLASSES": ["core.identity.IsIdentified"],
    "DEFAULT_RENDERER_CLASSES": ["rest_framework.renderers.JSONRenderer"],
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "EXCEPTION_HANDLER": "core.errors.api_exception_handler",
    "UNAUTHENTICATED_USER": None,
}

SPECTACULAR_SETTINGS = {
    "TITLE": "Agency Reports API",
    "VERSION": "0.1.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "COMPONENT_SPLIT_REQUEST": True,
}

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {"json": {"()": "core.logging.JsonFormatter"}},
    "handlers": {"console": {"class": "logging.StreamHandler", "formatter": "json"}},
    "root": {"handlers": ["console"], "level": ENV.log_level},
    "loggers": {
        # The request log in core.middleware replaces Django's own per-request lines.
        "django.server": {"level": "WARNING"},
        "django.request": {"level": "ERROR"},
    },
}

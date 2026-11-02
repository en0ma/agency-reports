"""Settings for pytest: same as settings.py, but runs without a backend/.env."""

import os

os.environ.setdefault("APP_ENV", "local")

from agency_reports.settings import *  # noqa: F403

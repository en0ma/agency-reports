import json
import logging
from datetime import datetime, timezone

# Attributes every LogRecord has; anything else was passed via `extra=` and goes into the JSON line.
_STANDARD = set(vars(logging.makeLogRecord({}))) | {"message", "asctime"}


class JsonFormatter(logging.Formatter):
    """One JSON object per line, so logs can be searched in Loki/Grafana the same way as the other services."""

    def format(self, record: logging.LogRecord) -> str:
        line = {
            "time": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(timespec="milliseconds"),
            "level": record.levelname.lower(),
            "logger": record.name,
            "msg": record.getMessage(),
        }
        line.update({key: value for key, value in vars(record).items() if key not in _STANDARD})
        if record.exc_info:
            line["exc"] = self.formatException(record.exc_info)
        return json.dumps(line, default=str)

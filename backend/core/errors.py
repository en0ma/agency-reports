from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import exception_handler


def api_exception_handler(exc: Exception, context: dict) -> Response | None:
    """Every non-2xx API response has the same body: `{"status_code", "error", "message"}`."""
    response = exception_handler(exc, context)
    if response is None:
        return None

    if isinstance(exc, ValidationError):
        message = _flatten(exc.detail)
    else:
        message = str(response.data.get("detail", "")) if isinstance(response.data, dict) else str(response.data)

    response.data = {
        "status_code": response.status_code,
        "error": response.status_text,
        "message": message,
    }
    return response


def _flatten(detail: object, prefix: str = "") -> str:
    if isinstance(detail, dict):
        return "; ".join(_flatten(value, f"{prefix}{key}: ") for key, value in detail.items())
    if isinstance(detail, list):
        return "; ".join(_flatten(item, prefix) for item in detail)
    return f"{prefix}{detail}"

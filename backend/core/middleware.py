import logging
import time
import uuid
from collections.abc import Callable

from django.http import HttpRequest, HttpResponse

log = logging.getLogger("agency_reports.request")

# Kubernetes probes call this constantly; keep them out of the request log.
QUIET_PATHS = {"/api/health"}


class RequestLogMiddleware:
    """Gives every request an id (echoed in the X-Request-Id response header) and logs one line when it completes."""

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        request.request_id = request.headers.get("X-Request-Id") or uuid.uuid4().hex[:12]
        started = time.perf_counter()
        response = self.get_response(request)

        response["X-Request-Id"] = request.request_id
        if request.path not in QUIET_PATHS:
            log.info(
                "request completed",
                extra={
                    "req_id": request.request_id,
                    "method": request.method,
                    "path": request.get_full_path(),
                    "status": response.status_code,
                    "duration_ms": round((time.perf_counter() - started) * 1000),
                },
            )
        return response

import json
import logging
import sys
import time

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.types import ASGIApp


class JSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_record: dict = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "service": "pdftrack-documents",
            "message": record.getMessage(),
            "logger": record.name,
        }
        for key in ("method", "path", "status_code", "duration_ms"):
            value = getattr(record, key, None)
            if value is not None:
                log_record[key] = value
        if record.exc_info and record.exc_info[0] is not None:
            log_record["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_record, default=str)


def setup_logging(level: str = "INFO") -> None:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JSONFormatter())
    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(getattr(logging, level.upper(), logging.INFO))


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app)
        self._logger = logging.getLogger("pdftrack-documents.access")

    async def dispatch(self, request: Request, call_next):  # type: ignore[override]
        start = time.perf_counter()
        response = await call_next(request)
        duration_ms = round((time.perf_counter() - start) * 1000, 2)
        self._logger.info(
            "%s %s %s",
            request.method,
            request.url.path,
            response.status_code,
            extra={
                "method": request.method,
                "path": str(request.url.path),
                "status_code": response.status_code,
                "duration_ms": duration_ms,
            },
        )
        return response

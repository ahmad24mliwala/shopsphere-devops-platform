import json
import logging
import sys
import time
from datetime import datetime, timezone

from fastapi import Request


class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "service": getattr(record, "service", "unknown"),
            "message": record.getMessage(),
        }

        for field in (
            "method",
            "path",
            "status_code",
            "duration_seconds",
        ):
            if hasattr(record, field):
                log_data[field] = getattr(record, field)

        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_data)


class ServiceLoggerAdapter(logging.LoggerAdapter):
    def process(self, msg, kwargs):
        extra = kwargs.get("extra", {})
        kwargs["extra"] = {**self.extra, **extra}
        return msg, kwargs


def setup_logging(service_name):
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JSONFormatter())

    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.addHandler(handler)
    root_logger.setLevel(logging.INFO)

    return ServiceLoggerAdapter(
        logging.getLogger(service_name),
        {"service": service_name},
    )


def setup_request_logging(app, logger):
    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        start_time = time.perf_counter()

        try:
            response = await call_next(request)
        except Exception:
            logger.exception(
                "HTTP request failed",
                extra={
                    "method": request.method,
                    "path": request.url.path,
                },
            )
            raise

        duration = time.perf_counter() - start_time

        route = request.scope.get("route")
        path = route.path if route else request.url.path

        logger.info(
            "HTTP request completed",
            extra={
                "method": request.method,
                "path": path,
                "status_code": response.status_code,
                "duration_seconds": round(duration, 4),
            },
        )

        return response

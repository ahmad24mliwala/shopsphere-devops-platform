import time

from fastapi import Request, Response
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    CollectorRegistry,
    Counter,
    Histogram,
    generate_latest,
)


def setup_metrics(app, service_name):
    registry = CollectorRegistry()

    requests_total = Counter(
        "http_requests_total",
        "Total HTTP requests",
        ["service", "method", "path", "status"],
        registry=registry,
    )

    request_duration = Histogram(
        "http_request_duration_seconds",
        "HTTP request duration in seconds",
        ["service", "method", "path"],
        registry=registry,
    )

    @app.middleware("http")
    async def collect_metrics(request: Request, call_next):
        if request.url.path == "/metrics":
            return await call_next(request)

        start_time = time.perf_counter()

        try:
            response = await call_next(request)
        except Exception:
            elapsed = time.perf_counter() - start_time
            request_duration.labels(
                service_name,
                request.method,
                request.url.path,
            ).observe(elapsed)

            requests_total.labels(
                service_name,
                request.method,
                request.url.path,
                "500",
            ).inc()
            raise

        elapsed = time.perf_counter() - start_time

        requests_total.labels(
            service_name,
            request.method,
            request.url.path,
            str(response.status_code),
        ).inc()

        request_duration.labels(
            service_name,
            request.method,
            request.url.path,
        ).observe(elapsed)

        return response

    @app.get("/metrics", include_in_schema=False)
    def metrics():
        return Response(
            content=generate_latest(registry),
            media_type=CONTENT_TYPE_LATEST,
        )

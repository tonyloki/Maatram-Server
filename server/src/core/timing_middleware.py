"""Request timing and observability middleware for Maatram FastAPI backend."""

import time

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from src.core.logging import logger


class RequestTimingMiddleware(BaseHTTPMiddleware):
    """Measures endpoint latency, attaches observability headers (X-Process-Time, Server-Timing),

    and emits structured logs for slow requests without leaking credentials or tokens.
    """

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        start_time = time.perf_counter()

        response = await call_next(request)

        process_time = time.perf_counter() - start_time
        process_time_ms = round(process_time * 1000, 2)

        # Inject standard latency observability headers
        response.headers["X-Process-Time"] = f"{process_time:.4f}"
        response.headers["Server-Timing"] = f"total;dur={process_time_ms}"

        path = request.url.path
        if process_time_ms > 200:
            logger.warning(
                f"Slow request detected: {request.method} {path} - {process_time_ms}ms "
                f"(Status: {response.status_code})"
            )
        else:
            logger.debug(
                f"Request completed: {request.method} {path} - {process_time_ms}ms "
                f"(Status: {response.status_code})"
            )

        return response


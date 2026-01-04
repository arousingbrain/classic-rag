import uuid
from typing import Callable

import structlog
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = structlog.get_logger()

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(request_id=request_id)

        logger.info("request_started", path=request.url.path, method=request.method)
        
        try:
            response = await call_next(request)
            logger.info("request_finished", status_code=response.status_code)
            response.headers["X-Request-ID"] = request_id
            return response
        except Exception as e:
            logger.exception("request_failed", error=str(e))
            raise

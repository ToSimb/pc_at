from starlette.middleware.base import BaseHTTPMiddleware
from logger.logger import logger


class LogMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        logger.info(f"method: {request.method} url: {request.url} status_code: {response.status_code}")
        return response
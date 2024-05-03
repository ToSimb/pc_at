from starlette.middleware.base import BaseHTTPMiddleware
from logger.logger import logger


class LogMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        logger.info(f"method: {request.method} client: {request.client.host} status_code: {response.status_code} url: {request.url}")
        return response
import logging
import time

from fastapi import Request


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

logger = logging.getLogger("gcet-assistant")


async def log_requests(request: Request, call_next):
    """
    Log every incoming request.
    """

    start_time = time.perf_counter()

    response = await call_next(request)

    duration = time.perf_counter() - start_time

    logger.info(
    "Method=%s | Path=%s | Status=%s | Duration=%.3fs | Client=%s",
    request.method,
    request.url.path,
    response.status_code,
    duration,
    request.client.host if request.client else "Unknown",
)

    return response
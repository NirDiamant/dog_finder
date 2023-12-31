import datetime
from typing import Any
import uuid
from app.MyLogger import logger
import time
import asyncio
import functools

def timeit(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        elapsed_time = time.time() - start_time
        logger.info(f"Execution time for {func.__name__}: {elapsed_time:.2f} seconds")

        return result

    return wrapper

def async_timeit(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = asyncio.get_event_loop().time()
        result = await func(*args, **kwargs)
        elapsed_time = asyncio.get_event_loop().time() - start_time
        logger.info(f"Execution time for {func.__name__}: {elapsed_time:.2f} seconds")

        return result

    return wrapper

def _json_serializable(value: Any) -> Any:
    if isinstance(value, datetime.datetime):
        return value.isoformat()
    return value

def generate_dog_id():
    return str(uuid.uuid4())
from app.MyLogger import logger
import regex as re
import html
import time
import asyncio
import functools
import base64
import imghdr

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

def detect_image_mimetype(base64_str):
    img_data = base64.b64decode(base64_str)
    
    return imghdr.what(None, img_data)
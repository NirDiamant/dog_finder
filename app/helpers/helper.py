import datetime
import hashlib
from typing import Any
import uuid
from app.MyLogger import logger
import regex as re
import html
import time
import asyncio
import functools
import base64
import imghdr
import io
from PIL import Image

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

def hash_image(image):
    return hashlib.md5(image.encode()).hexdigest()

def generate_dog_id():
    return str(uuid.uuid4())

def detect_image_mimetype(base64_str):
    img_data = base64.b64decode(base64_str)
    
    return imghdr.what(None, img_data)

def resize_image_and_convert_to_format(base64_str: str, max_size: tuple[int, int], format: str = "WEBP") -> (str, str):
    """
    Resize an image represented as a base64 string and convert it to a specified format.

    Args:
        base64_str (str): The base64-encoded string representation of the image.
        max_size (tuple[int, int]): The maximum width and height of the resized image.
        format (str, optional): The format to convert the image to. Defaults to "WEBP".

    Returns:
        tuple: A tuple containing the resized image as a base64 string and the image format.
    """
    # Decode the base64 string into image data
    img_data = base64.b64decode(base64_str)

    # Open the image from the image data
    img = Image.open(io.BytesIO(img_data))

    # Check if the image needs to be resized, if not just convert it to the specified format
    width, height = img.size
    max_width, max_height = max_size
    if width <= max_width and height <= max_height:
        buffered = io.BytesIO()
        img.save(buffered, format=format)

        # Encode the resized image as a base64 string and return it along with the image format
        return base64.b64encode(buffered.getvalue()).decode('utf-8'), f"image/{format.lower()}"

    # Calculate the new size while maintaining aspect ratio
    ratio = min(max_width / width, max_height / height)
    new_size = (int(width * ratio), int(height * ratio))

    # Resize the image and return as base64 string
    img = img.resize(new_size)
    buffered = io.BytesIO()
    img.save(buffered, format=format)

    # Encode the resized image as a base64 string and return it along with the image format
    return base64.b64encode(buffered.getvalue()).decode('utf-8'), f"image/{format.lower()}"
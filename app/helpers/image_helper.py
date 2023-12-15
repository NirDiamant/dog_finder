import hashlib
import imghdr
import io
from app.MyLogger import logger
from typing import List
from PIL import Image
from io import BytesIO
import base64

def get_base64(img_content):
    img_base64 = base64.b64encode(img_content).decode('utf-8')
    logger.debug(f"Image base64: {img_base64}")

    return img_base64

def create_pil_images(base64Images: List[str]):
    # Open the images from the base64 strings to PIL Images
    pil_images = []
    for img_base64 in base64Images:
        pil_image = Image.open(BytesIO(base64.b64decode(img_base64)))
        pil_images.append(pil_image)
        
    return pil_images

def pil_image_to_base64(pil_image):
    buffered = BytesIO()
    pil_image.save(buffered, format="WEBP")
    img_str = base64.b64encode(buffered.getvalue())
    
    return img_str.decode('utf-8')

def hash_image(image):
    return hashlib.md5(image.encode()).hexdigest()

# def resize_image(img: Image, max_size: tuple[int, int]) -> Image:
#     """
#     Resize an image if its dimensions exceed the maximum size.

#     Args:
#         img (Image): The image to resize.
#         max_size (tuple[int, int]): The maximum width and height of the resized image.

#     Returns:
#         Image: The resized image.
#     """
#     # Check if the image needs to be resized
#     width, height = img.size
#     max_width, max_height = max_size

#     # If the image needs resized, resize it
#     if width > max_width or height > max_height:
#         # Calculate the new size while maintaining aspect ratio
#         ratio = min(max_width / width, max_height / height)
#         new_size = (int(width * ratio), int(height * ratio))
#         # Resize the image and return it
#         img = img.resize(new_size)
    
#     return img


def detect_image_mimetype(base64_str):
    img_data = base64.b64decode(base64_str)
    
    return imghdr.what(None, img_data)

def resize_image_if_needed(base64_str: str, max_size: tuple[int, int]) -> (str, str):
    """
    Resize an image represented as a base64 string if it exceeds the max size.

    Args:
        base64_str (str): The base64-encoded string representation of the image.
        max_size (tuple[int, int]): The maximum width and height of the resized image.

    Returns:
        str: The resized image as a base64 string.
    """
    # Decode the base64 string into image data
    img_data = base64.b64decode(base64_str)

    # Open the image from the image data
    img = Image.open(io.BytesIO(img_data))

    # Check if the image needs to be resized
    width, height = img.size
    max_width, max_height = max_size

    if width > max_width or height > max_height:
        # Calculate the new size while maintaining aspect ratio
        ratio = min(max_width / width, max_height / height)
        new_size = (int(width * ratio), int(height * ratio))

        # Resize the image
        img = img.resize(new_size)
        
    # Check if the image format is webp, return it as is
    elif img.format == format:
        return base64_str, f"image/webp"

    buffered = io.BytesIO()
    img.save(buffered, format="WEBP")

    # Encode the resized image as a base64 string and return it
    return base64.b64encode(buffered.getvalue()).decode('utf-8'), f"image/webp"

def convert_image_to_webp(base64_str: str) -> (str, str):
    """
    Convert an image represented as a base64 string to WEBP format.

    Args:
        base64_str (str): The base64-encoded string representation of the image.

    Returns:
        str: The image in WEBP format as a base64 string.
    """
    # Decode the base64 string into image data
    img_data = base64.b64decode(base64_str)

    # Open the image from the image data
    img = Image.open(io.BytesIO(img_data))

    # If the image format is already WEBP, return it as is
    if img.format == "WEBP":
        return base64_str, f"image/webp"

    buffered = io.BytesIO()
    img.save(buffered, format="WEBP")

    # Encode the image as a base64 string and return it
    return base64.b64encode(buffered.getvalue()).decode('utf-8'), f"image/webp"

# Write a function that get a pil image, converts it to webp pil image and returns the new image
def convert_pil_image_to_webp(pil_image: Image) -> Image:
    """
    Convert a PIL image to WEBP format.

    Args:
        pil_image (Image): The PIL image to convert.

    Returns:
        Image: The image in WEBP format.
    """
    # If the image format is already WEBP, return it as is
    if pil_image.format == "WEBP":
        return pil_image

    buffered = io.BytesIO()
    pil_image.save(buffered, format="WEBP")

    # Encode the image as a base64 string and return it
    return Image.open(buffered)


def resize_and_convert(base64_str: str, max_size: tuple[int, int]) -> (str, str):
    """
    Resize an image if needed and convert it to WEBP format.

    Args:
        base64_str (str): The base64-encoded string representation of the image.
        max_size (tuple[int, int]): The maximum width and height of the resized image.

    Returns:
        str: The resized image in WEBP format as a base64 string.
    """
    resized_image, _format = resize_image_if_needed(base64_str, max_size)
    
    return convert_image_to_webp(resized_image)
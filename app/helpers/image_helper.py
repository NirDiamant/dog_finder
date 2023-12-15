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
    pil_image.save(buffered, format="JPEG")
    img_str = base64.b64encode(buffered.getvalue())
    
    return img_str.decode('utf-8')

def resize_image(img: Image, max_size: tuple[int, int]) -> Image:
    """
    Resize an image if its dimensions exceed the maximum size.

    Args:
        img (Image): The image to resize.
        max_size (tuple[int, int]): The maximum width and height of the resized image.

    Returns:
        Image: The resized image.
    """
    # Check if the image needs to be resized
    width, height = img.size
    max_width, max_height = max_size

    # If the image needs resized, resize it
    if width > max_width or height > max_height:
        # Calculate the new size while maintaining aspect ratio
        ratio = min(max_width / width, max_height / height)
        new_size = (int(width * ratio), int(height * ratio))
        # Resize the image and return it
        img = img.resize(new_size)
    
    return img
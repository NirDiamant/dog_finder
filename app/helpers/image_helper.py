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
# Import packages
import cv2
import numpy as np
from PIL import Image
import torch

from app.helpers.image_helper import convert_image_to_webp, convert_pil_image_to_webp


def find_largest_blob_among_masks(mask_list):
    """
    Finds the largest blob among a list of boolean masks.

    Args:
    mask_list (list of numpy.ndarray): A list of boolean masks.

    Returns:
    numpy.ndarray: The mask containing the largest blob among all masks.
    """
    largest_blob_mask = None
    max_size = 0

    for boolean_mask in mask_list:
        # Convert boolean mask to uint8
        mask_uint8 = np.uint8(boolean_mask) * 255

        # Find connected components
        num_labels, labels_im = cv2.connectedComponents(mask_uint8)

        for i in range(1, num_labels):
            size = np.sum(labels_im == i)
            if size > max_size:
                max_size = size
                largest_blob_mask = (labels_im == i)

    # Handle case where no blobs were found
    if largest_blob_mask is None:
        raise ValueError("No blobs found in any of the masks")

    return largest_blob_mask

def create_masked_image(pil_image, boolean_mask, background_color=(0, 0, 0)):
    """
    Create a new image that contains only the area of the mask. The original image is a PIL image,
    and the mask is a boolean NumPy array.

    Args:
    pil_image (PIL.Image.Image): The original PIL image.
    boolean_mask (numpy.ndarray): The boolean mask to apply.
    background_color (tuple): The color for the background (outside the mask). Default is black.

    Returns:
    PIL.Image.Image: The new PIL image with only the masked area.
    """
    # Convert PIL image to NumPy array
    image = np.array(pil_image)

    if image.shape[:2] != boolean_mask.shape:
        raise ValueError("The dimensions of the image and the mask must match")

    # Convert boolean mask to uint8 binary mask
    binary_mask = np.uint8(boolean_mask) * 255

    # Apply the mask to keep only the masked area
    masked_area = cv2.bitwise_and(image, image, mask=binary_mask)

    # Create an inverse mask for the background
    inverse_mask = cv2.bitwise_not(binary_mask)

    # Create a background image with the specified color
    background = np.full(image.shape, background_color, dtype=np.uint8)

    # Apply the inverse mask to the background image
    background = cv2.bitwise_and(background, background, mask=inverse_mask)

    # Combine the masked area and the background
    combined_image = cv2.add(masked_area, background)

    # Convert back to PIL image
    result_image = Image.fromarray(combined_image)

    return result_image

def process_pil_image(pil_image, text_prompt="a dog", image_segmentation_model=None):
    """
    Process a PIL image to find and mask the largest blob matching the text prompt.
    Args:
    image_pil (PIL.Image.Image): The PIL image to process.
    text_prompt (str): Text prompt for object detection.
    Returns:
    PIL.Image.Image: The processed PIL image.
    """

    masks, boxes, phrases, logits = image_segmentation_model.predict(pil_image, text_prompt)

    if len(masks) == 0:
        print(f"No objects of the '{text_prompt}' prompt detected in the image.")
        return None
    
    masks_np = [mask.squeeze().cpu().numpy() for mask in masks]
    mask_np = find_largest_blob_among_masks(masks_np)
    masked_im = create_masked_image(pil_image, mask_np)
    
    return masked_im

def process_pil_image_YOLO(pil_image, image_segmentation_model):
    # Run inference on the image
    results = image_segmentation_model(pil_image, retina_masks=True, classes=16)  # Class 16 for dogs in COCO
    for result in results:
        masks = result.masks.data  # get array results
        boxes = result.boxes.data
        clss = boxes[:, 5]  # extract classes
        dog_indices = torch.where(clss == 16)  # indices of dog detections
        dog_masks = masks[dog_indices]  # relevant masks for dogs
        dog_mask = torch.any(dog_masks, dim=0).int() * 255  # combine masks
        dog_mask = dog_mask.squeeze().cpu().numpy()
        
        image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
        if image.shape[:2] != dog_mask.shape:
            raise ValueError("The dimensions of the image and the mask must match")

        # Convert dog_mask to uint8 binary mask
        binary_mask = np.uint8(dog_mask)

        # Apply the mask to keep only the masked area
        masked_area = cv2.bitwise_and(image, image, mask=binary_mask)

        # Create an inverse mask for the background
        inverse_mask = cv2.bitwise_not(binary_mask)

        # Create a background image with the specified color
        background = np.full(image.shape, (0, 0, 0), dtype=np.uint8)

        # Apply the inverse mask to the background image
        background = cv2.bitwise_and(background, background, mask=inverse_mask)

        # Combine the masked area and the background
        combined_image = cv2.add(masked_area, background)
        combined_image = Image.fromarray(cv2.cvtColor(combined_image, cv2.COLOR_BGR2RGB))
        combined_image = convert_pil_image_to_webp(combined_image)
        
        return combined_image

from typing import List
from PIL import Image
import torch
import torchvision.transforms as transforms

class FeatureExtractor:
    def __init__(self):
        # Set the device to GPU if available
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        # Load the DINO model
        try:
            self.dino = torch.hub.load("facebookresearch/dinov2", "dinov2_vitb14")
        except Exception as e:
            print(f"Error loading model: {e}")
            exit(1)

        self.dino.to(self.device)
        self.dino.eval()

        # Define the image transformations
        self.image_transforms = transforms.Compose(
            [
                transforms.Resize((224, 224)),
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
            ]
        )

    from typing import Union

    def encode(self, pil_images: Union[Image.Image, List[Image.Image]]):
        """
        Extract features from a PIL image or a list of PIL images using the DINO model.

        Args:
        pil_images (Union[PIL.Image, List[PIL.Image]]): A PIL image or a list of PIL images.

        Returns:
        List[torch.Tensor]: Extracted feature tensors.
        """
        if isinstance(pil_images, Image.Image):
            pil_images_list = [pil_images]
        else:
            pil_images_list = pil_images

        features_list = []
        for pil_image in pil_images_list:
            image = pil_image.convert("RGB")
            image_tensor = self.image_transforms(image).unsqueeze(0).to(self.device)
            with torch.no_grad():
                features = self.dino(image_tensor).float()

            # Free GPU memory if used
            if self.device.type == 'cuda':
                torch.cuda.empty_cache()

            features_list.append(features[0].tolist())

        if isinstance(pil_images, Image.Image):
            return features_list[0]
        else:
            return features_list

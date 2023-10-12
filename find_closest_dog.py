import os
import torch
import cv2
import heapq
from utils import to_vgg_input
from vgg_processing import get_vgg_features, get_l2_vgg_features, get_cosine_similarity

class DogSimilarityFinder:
    def __init__(self, device, vgg_model):
        """
        Initializes the DogSimilarityFinder with a specified device and VGG model.
        
        Args:
            device (torch.device): The device to use for computations (CPU or CUDA).
            vgg_model (torch.nn.Module): The pretrained VGG model to use for feature extraction.
        """
        self.device = device
        self.vgg_model = vgg_model

    def find_k_closest_dogs(self, img, vgg_features_dict, k, similarity_func=get_l2_vgg_features):
        """
        Identifies the k most similar dogs to a given image based on their VGG-16 features.
        
        Args:
            img (ndarray): The input image of a dog.
            vgg_features_dict (dict): A dictionary containing dog images and their corresponding VGG-16 features.
            k (int): The number of most similar dogs to find.
            similarity_func (callable): The function to use for computing similarity (distance) between feature vectors.
        
        Returns:
            list: A list of tuples containing the negative distance, VGG-16 features, and image of one of the k most similar dogs.
        """
        img_tensor = to_vgg_input(img)
        img_vgg_features = get_vgg_features(img_tensor, self.vgg_model)
        closest_dogs_heap = []
        for _, value in vgg_features_dict.items():
            dog_imgs, dog_features = value
            vgg_dist = similarity_func(img_vgg_features, dog_features)
            if len(closest_dogs_heap) < k:
                heapq.heappush(closest_dogs_heap, (-vgg_dist, dog_features, dog_imgs))
            else:
                heapq.heappushpop(closest_dogs_heap, (-vgg_dist, dog_features, dog_imgs))
        closest_dogs_list = [(-dist, dog_features, dog_img) for dist, dog_features, dog_img in closest_dogs_heap]
        closest_dogs_list.sort(key=lambda x: x[0])
        return closest_dogs_list

    def add_to_dict(self, img, img_features_dict):
        """
        Adds the given image and its VGG-16 features to the given dictionary.
        
        Args:
            img (ndarray): The image to add.
            img_features_dict (dict): The dictionary to which the image and its features should be added.
        """
        img_vgg_features = get_vgg_features(to_vgg_input(img), self.vgg_model)
        img_features_dict[len(img_features_dict)] = (img, img_vgg_features)

    def create_lost_dict(self, lost_dir):
        """
        Creates a dictionary containing images and their VGG-16 features from the specified directory.
        
        Args:
            lost_dir (str): The directory path containing the images.
        
        Returns:
            dict: A dictionary where the keys are incremental integers and the values are tuples containing the image and its VGG-16 features.
        """
        img_features_dict_lost = {}
        images_lost = os.listdir(lost_dir)
        for img_path in images_lost:
            img = cv2.imread(os.path.join(lost_dir, img_path))
            self.add_to_dict(img, img_features_dict_lost)
        return img_features_dict_lost

def main():
    """
    Entry point of the script to find the k most similar dogs for a given image based on their VGG-16 features.

    - Define the directories for found, lost, and mixed lost dog images.
    - Create a dictionary of images and their VGG-16 features for the mixed lost dog images.
    - Load the found dog images.
    - Read the first found dog image and find the k most similar dogs among the mixed lost dog images.
    - Extract and list the images of the k most similar dogs.
    """
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    vgg16 = torch.hub.load('pytorch/vision:v0.10.0', 'vgg16', pretrained=True).eval().to(device)
    dog_similarity_finder = DogSimilarityFinder(device, vgg16)
    
    # Define the directories for found, lost, and mixed lost dog images
    images_found_dir = 'C:\\Users\\N7\\Downloads\\images\\Images\\n02085620-Chihuahua\\found'
    images_lost_dir = 'C:\\Users\\N7\\Downloads\\images\\Images\\n02085620-Chihuahua\\lost'
    mix_lost_dir = 'C:\\Users\\N7\\Downloads\\images\\Images\\n02085620-Chihuahua\\mix_lost'

    # Create a dictionary of images and their VGG-16 features for the mixed lost dog images
    img_features_dict_lost = dog_similarity_finder.create_lost_dict(mix_lost_dir)

    # Load the found dog images
    images_found = os.listdir(images_found_dir)

    # Read the first found dog image
    first_found = cv2.imread(os.path.join(images_found_dir, images_found[0]))

    # Set the number of most similar dogs to find
    num_closest_dogs = 5

    # Find the k most similar dogs among the mixed lost dog images
    closest_dogs_list = dog_similarity_finder.find_k_closest_dogs(first_found, img_features_dict_lost, k=num_closest_dogs)

    # Extract and list the images of the k most similar dogs
    closest_images_list = [dog_img for _, _, dog_img in closest_dogs_list]
    print("")

if __name__ == '__main__':
    main()

import os
import torch
import cv2
import heapq
import copy

from utils import to_vgg_input
from vgg_processing import get_vgg_features, get_l2_vgg_features


device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
vgg16 = torch.hub.load('pytorch/vision:v0.10.0', 'vgg16', pretrained=True).eval().to(device)


def find_k_closest_dogs(img, vgg_features_dict, k):
    """
    This function identifies the k most similar dogs to a given image based on their VGG-16 features.
    
    Args:
        img (ndarray): The input image of a dog.
        vgg_features_dict (dict): A dictionary where each value is a tuple containing an image of a dog
                                  and its corresponding VGG-16 features.
        k (int): The number of most similar dogs to find.
    
    Returns:
        list: A list of tuples, each containing the negative distance, VGG-16 features, and image of one
              of the k most similar dogs. The list is sorted in ascending order of negative distance, so 
              the most similar dog is first in the list.
    
    The function processes the input image to obtain its VGG-16 features, then iterates through
    vgg_features_dict to compute the distance between the input image's features and each dog's
    features in vgg_features_dict. A min-heap is used to efficiently keep track of the k smallest
    distances (i.e., the k most similar dogs). Finally, the function sorts the k most similar dogs
    by distance and returns them in a list.
    """
    # Convert the input image to the required format for VGG and get its features
    img_tensor = to_vgg_input(img)
    img_vgg_features = get_vgg_features(img_tensor, vgg16)

    # Use a heap to keep track of the k smallest distances
    # The heap will contain tuples of (-distance, dog_features, dog_img)
    # Negate the distances since heapq is a min-heap and we want to keep the k largest distances
    closest_dogs_heap = []

    for _, value in vgg_features_dict.items():
        dog_imgs, dog_features = value
        vgg_dist = get_l2_vgg_features(img_vgg_features, dog_features)
        if len(closest_dogs_heap) < k:
            # If the heap has fewer than k items, add the current item
            heapq.heappush(closest_dogs_heap, (-vgg_dist, dog_features.clone(), copy.deepcopy(dog_imgs)))
        else:
            # If the heap has k items, add the current item and remove the smallest item
            heapq.heappushpop(closest_dogs_heap, (-vgg_dist, dog_features.clone(), copy.deepcopy(dog_imgs)))

    # Convert the heap to a list of (dog_img, dog_features) tuples and sort by distance
    # Negate the distances again to get positive distances
    closest_dogs_list = [(-dist, dog_features, dog_img) for dist, dog_features, dog_img in closest_dogs_heap]
    closest_dogs_list.sort(key=lambda x: x[0])

    return closest_dogs_list




def add_to_dict(img, img_features_dict):
    """
    Adds the given image and its VGG-16 features to the given dictionary.
    
    Args:
        img (ndarray): The image to add.
        img_features_dict (dict): The dictionary to which the image and its features should be added.
    """
    img_vgg_features = get_vgg_features(to_vgg_input(img), vgg16)
    img_features_dict[len(img_features_dict)] = (img, img_vgg_features)



def create_lost_dict(lost_dir):
    """
    Creates a dictionary containing the images and their VGG-16 features 
    from the specified directory.

    Args:
        lost_dir (str): The directory path containing the images.

    Returns:
        dict: A dictionary where the keys are incremental integers starting from 0, 
              and the values are tuples containing the image and its VGG-16 features.

    Usage:
        This function can be used to process a directory of images, extract their
        VGG-16 features, and organize this data into a dictionary for later use,
        such as comparing these features to those of other images to find matches.
    """
    img_features_dict_lost = {}  # Initialize an empty dictionary to store the images and features
    images_lost = os.listdir(lost_dir)  # List all files in the specified directory
    for img_path in images_lost:  # Iterate through each file in the directory
        img = cv2.imread(os.path.join(lost_dir,img_path))  # Read the image file
        add_to_dict(img, img_features_dict_lost)  # Add the image and its features to the dictionary
    return img_features_dict_lost  # Return the dictionary containing the images and their features



def main():
    """
    Entry point of the script to find the k most similar dogs for a given image based on their VGG-16 features.

    - Define the directories for found, lost, and mixed lost dog images.
    - Create a dictionary of images and their VGG-16 features for the mixed lost dog images.
    - Load the found dog images.
    - Read the first found dog image and find the k most similar dogs among the mixed lost dog images.
    - Extract and list the images of the k most similar dogs.

    Directories:
        images_found_dir (str): Directory path containing images of found dogs.
        images_lost_dir (str): Directory path containing images of lost dogs.
        mix_lost_dir (str): Directory path containing images of mixed lost dogs.
    
    Variables:
        img_features_dict_lost (dict): A dictionary of images and their VGG-16 features for the mixed lost dogs.
        images_found (list): A list of image filenames for the found dogs.
        first_found (ndarray): The first image in the list of found dog images.
        num_closest_dogs (int): The number of most similar dogs to find.
        closest_dogs_list (list): A list of tuples, each containing the VGG-16 features and image of one of the k most similar dogs.
        closest_images_list (list): A list of images of the k most similar dogs.
    """

    # Define the directories for found, lost, and mixed lost dog images
    images_found_dir = 'C:\\Users\\N7\\Downloads\\images\\Images\\n02085620-Chihuahua\\found'
    images_lost_dir = 'C:\\Users\\N7\\Downloads\\images\\Images\\n02085620-Chihuahua\\lost'
    mix_lost_dir = 'C:\\Users\\N7\\Downloads\\images\\Images\\n02085620-Chihuahua\\mix_lost'

    # Create a dictionary of images and their VGG-16 features for the mixed lost dog images
    img_features_dict_lost = create_lost_dict(mix_lost_dir)

    # Load the found dog images
    images_found = os.listdir(images_found_dir)

    # Read the first found dog image
    first_found = cv2.imread(os.path.join(images_found_dir,images_found[0]))

    # Set the number of most similar dogs to find
    num_closest_dogs = 5

    # Find the k most similar dogs among the mixed lost dog images
    closest_dogs_list = find_k_closest_dogs(first_found, img_features_dict_lost, k=num_closest_dogs)

    # Extract and list the images of the k most similar dogs
    closest_images_list = [dog_img for _,_, dog_img in closest_dogs_list]

if __name__ == '__main__':
    main()


import torch
import torch.nn.functional as F

# Set the device for torch operations
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")


def get_vgg_features(im, vgg16):
    """
    Processes an image tensor, resizes it to 256x256, and extracts its features using a VGG-16 model.
    
    Args:
        im (torch.Tensor): The input image tensor.
        vgg16 (torch.nn.Module): The VGG-16 model.
    
    Returns:
        torch.Tensor: The VGG-16 features of the input image.
    
    This function performs the following steps:
        1. Scales the input image tensor from the range [-1, 1] to [0, 255].
        2. Resizes the image tensor to 256x256 using area interpolation.
        3. Feeds the processed image tensor through the VGG-16 model to extract its features.
    """
    im = (im + 1) * (255 / 2)  # Scale the image tensor from [-1, 1] to [0, 255]
    im = F.interpolate(im, size=(256, 256), mode='area')  # Resize the image tensor to 256x256
    im_features = vgg16(im)  # Extract VGG-16 features
    return im_features


def get_l2_vgg_features(vgg_features1, vgg_features2):
    """
    Computes the L2 distance between the VGG-16 features of two images.
    
    Args:
        vgg_features1 (torch.Tensor): The VGG-16 features of the first image.
        vgg_features2 (torch.Tensor): The VGG-16 features of the second image.
    
    Returns:
        float: The L2 distance between the VGG-16 features of the two images.
    
    The function computes the L2 distance (Euclidean distance) between two sets of VGG-16 features
    by subtracting each feature value in vgg_features1 from the corresponding feature value in 
    vgg_features2, squaring the result, summing all the squared differences, and returning the sum.
    """
    return (vgg_features1 - vgg_features2).square().sum().item()  # Compute and return the L2 distance





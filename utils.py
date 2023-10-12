import torch
import pickle


def to_vgg_input(img):
    """
    Converts an image array to a torch tensor and adjusts the dimensions for VGG input.
    
    Args:
        img (ndarray): The input image array.
    
    Returns:
        torch.Tensor: The input image tensor with dimensions adjusted for VGG input.
    """
    return torch.from_numpy(img).permute(2, 0, 1).unsqueeze(0)



def save_obj(obj, name):
    """
    Saves an object to a file using pickle.
    
    Args:
        obj (object): The object to save.
        name (str): The name of the object, which will be used as the file name.
    
    The function saves the object to a file with a '.pkl' extension using pickle's highest protocol.
    """
    with open(str(name) + '.pkl', 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)



def load_obj(name):
    """
    Loads an object from a file using pickle.
    
    Args:
        name (str): The name of the object, which corresponds to the file name.
    
    Returns:
        object: The loaded object.
    
    The function loads an object from a file with a '.pkl' extension using pickle.
    """
    with open(str(name) + '.pkl', 'rb') as f:
        return pickle.load(f)


















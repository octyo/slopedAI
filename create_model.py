import torch
import torch.nn as nn

# Type stuff
from torch.nn.modules.container import Sequential

def create_model(channels=3):
    return nn.Sequential(
        nn.Conv2d(channels, 16, kernel_size=3, stride=1, padding=1),
        nn.Dropout2d(0.1),
        nn.ReLU(),
        nn.MaxPool2d(kernel_size=2),
        nn.Conv2d(16, 32, kernel_size=3, stride=1, padding=1),
        nn.Dropout2d(0.1),
        nn.ReLU(),
        nn.MaxPool2d(kernel_size=2),
        nn.Conv2d(32, 64, kernel_size=3, stride=1, padding=1),
        nn.Dropout2d(0.1),
        nn.ReLU(),
        nn.MaxPool2d(kernel_size=2),
        nn.Flatten(),
        nn.Linear(64 * 4 * 4, 500),
        nn.Dropout2d(0.1),
        nn.ReLU(),
        nn.Linear(500, 3)
        # Softmax?
    )


def gaussian_noise(model: Sequential, sigma=0.001) -> Sequential:
    """Takes a torch model and returns a mutated model made via the gaussian noise evolution strategy"""

    new_model = create_model()

    new_params = []

    for p in model.parameters():
        rand_tensor = p * torch.randn(*p.shape) * sigma**(1/2)
        # print(rand_tensor.round(decimals=3))
        new_params.append(p + rand_tensor)


    # Load the parameters into the new model's state_dict
    state_dict = new_model.state_dict()  # Get the new model's state_dict
    state_keys = list(state_dict.keys())  # Get parameter names in the state_dict
    
    # Assign new parameter values
    for key, new_param in zip(state_keys, new_params):
        state_dict[key] = new_param
    
    # Load the updated state_dict into the new model
    new_model.load_state_dict(state_dict)

    return new_model

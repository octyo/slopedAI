import torch
import torch.nn as nn

# Type stuff
from torch.nn.modules.container import Sequential

def model_1(channels=3):
    return nn.Sequential(
        nn.Conv2d(channels, 20, kernel_size=5), # 64x64x3 -> 60x60x20
        nn.ReLU(),
        nn.MaxPool2d(kernel_size=2), # 60x60x20 -> 30x30x20

        nn.Flatten(), # 30x30x20 -> 30*30*20

        nn.Linear(30*30*20, 500),
        nn.ReLU(),

        nn.Linear(500, 3)
    )

def model_2(channels=3):
    return nn.Sequential(
        nn.Conv2d(channels, 20, kernel_size=5), # 64x64x3 -> 60x60x20
        nn.ReLU(),
        nn.MaxPool2d(kernel_size=2), # 60x60x20 -> 30x30x20

        nn.Conv2d(20, 50, kernel_size=5), # 30x30x20 -> 26x26x50
        nn.ReLU(),
        nn.MaxPool2d(kernel_size=2), # 26x26x50 -> 13x13x50

        nn.Flatten(), # 13x13x50 -> 13*13*50

        nn.Linear(13*13*50, 500),
        nn.ReLU(),

        nn.Linear(500, 3)
    )

def model_3(channels=3):
    return nn.Sequential(
        nn.Conv2d(channels, 20, kernel_size=5), # 64x64x3 -> 60x60x20
        nn.ReLU(),
        nn.MaxPool2d(kernel_size=2), # 60x60x20 -> 30x30x20

        nn.Conv2d(20, 50, kernel_size=5), # 30x30x20 -> 26x26x50
        nn.ReLU(),
        nn.MaxPool2d(kernel_size=2), # 26x26x50 -> 13x13x50

        nn.Conv2d(50, 50, kernel_size=5), # 13x13x50 -> 9x9x50
        nn.ReLU(),
        nn.MaxPool2d(kernel_size=2), # 9x9x50 -> 4x4x50

        nn.Flatten(), # 4x4x50 -> 4*4*50

        nn.Linear(4*4*50, 500),
        nn.ReLU(),

        nn.Linear(500, 3)
    )

def gaussian_noise(model: Sequential, sigma=0.001, model_creator=model_3) -> Sequential:
    """Takes a torch model and returns a mutated model made via the gaussian noise evolution strategy"""

    new_model = model_creator()

    new_params = []
    
    model.to("cpu") # Bring model back to cpu
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


def crossover(model1: Sequential, model2: Sequential, model_creator) -> Sequential:
    """Takes two models as argument and returns a random parameter mix, where a given parameter in the new model is either from model1 og model2."""

    new_model = model_creator()

    new_params = []

    model1.to("cpu") # Bring model back to cpu
    model2.to("cpu") # Bring model back to cpu
    model1_params = [p for p in model1.parameters()]
    model2_params = [p for p in model2.parameters()]

    for i in range(len(model1_params)):
        shape = model1_params[i].shape
        bool_tensor = torch.randint(0, 2, size=shape, dtype=torch.bool)

        new_params.append(model1_params[i] * bool_tensor + model2_params[i] * ~bool_tensor)


    # Load the parameters into the new model's state_dict
    state_dict = new_model.state_dict()  # Get the new model's state_dict
    state_keys = list(state_dict.keys())  # Get parameter names in the state_dict
    
    # Assign new parameter values
    for key, new_param in zip(state_keys, new_params):
        state_dict[key] = new_param
    
    # Load the updated state_dict into the new model
    new_model.load_state_dict(state_dict)

    return new_model
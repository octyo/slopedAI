import torch
import torch.nn as nn

# Type stuff
from torch.nn.modules.container import Sequential

def create_model(channels=1):
    return nn.Sequential(
        nn.Conv2d(channels, 16, kernel_size=3, stride=1, padding=1), # 64x64x1 -> 64x64x16
        nn.ReLU(),
        nn.MaxPool2d(kernel_size=2), # 64x64x16 -> 32x32x16

        nn.Conv2d(16, 32, kernel_size=3, stride=1, padding=1), # 32x32x16 -> 32x32x32
        nn.ReLU(),
        nn.MaxPool2d(kernel_size=2), # 32x32x32 -> 16x16x32

        nn.Conv2d(32, 64, kernel_size=3, stride=1, padding=1), # 16x16x32 -> 16x16x64
        nn.ReLU(),
        nn.MaxPool2d(kernel_size=2), # 16x16x64 -> 8x8x64

        nn.Flatten(), # 8x8x64 -> 64*8*8

        nn.Linear(64*8*8, 500),
        nn.ReLU(),

        nn.Linear(500, 3)
        # Softmax?
    )


def gaussian_noise(model: Sequential, sigma=0.001) -> Sequential:
    """Takes a torch model and returns a mutated model made via the gaussian noise evolution strategy"""

    new_model = create_model()

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


def crossover(model1: Sequential, model2: Sequential) -> Sequential:
    """Takes two models as argument and returns a random parameter mix, where a given parameter in the new model is either from model1 og model2."""

    new_model = create_model()

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
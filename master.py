import torch
import torch.nn as nn
import torchvision.transforms as transforms
import PIL
import numpy as np

# Broswer control called
# broswerfunctionshi(model) -> reward

# Define model, evolution based approach right now
def create_model():
    return nn.Sequential(
        nn.Conv2d(3, 16, kernel_size=3, stride=1, padding=1),
        nn.Dropout2d(0.1),
        nn.ReLU(),
        nn.MaxPool2d(kernel_size=2, stride=2),
        nn.Conv2d(16, 32, kernel_size=3, stride=1, padding=1),
        nn.Dropout2d(0.1),
        nn.ReLU(),
        nn.MaxPool2d(kernel_size=2, stride=2),
        nn.Conv2d(32, 64, kernel_size=3, stride=1, padding=1),
        nn.Dropout2d(0.1),
        nn.ReLU(),
        nn.MaxPool2d(kernel_size=2, stride=2),
        nn.Flatten(),
        nn.Linear(64 * 4 * 4, 500),
        nn.Dropout2d(0.1),
        nn.ReLU(),
        nn.Linear(500, 3)
        # Softmax?
    )

population = [create_model() for i in range(10)]

models_per_run = 5

while True:
    rewards = []
    for model in population:
        reward = broswerfunctionshi(model)
        rewards.append(reward)
    # Sort by rewards
    population = [population[i] for i in np.argsort(rewards)]
    # Keep top models
    population = population[:models_per_run]
    # Mutate models
    for i in range(1, models_per_run):
        population.append(population[i].copy())
        for param in population[-1].parameters():
            param.data += torch.randn_like(param.data) * 0.1
    

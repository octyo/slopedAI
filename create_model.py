import torch
import torch.nn as nn
import torchvision.transforms as transforms
import PIL
import numpy as np


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
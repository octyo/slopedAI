import torch
import torch.nn as nn
import torchvision.transforms as transforms
import PIL
import numpy as np

import GameController
from create_model import create_model

# Loop start

# Define CNN model
policy = create_model()
ins_per_run = 5

while True:
    for
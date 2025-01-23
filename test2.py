import os
import torch
from master import read_model

# Load the model
print("Loading model")
model = read_model(10, 1)
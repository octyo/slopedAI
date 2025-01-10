import torch
import torch.nn as nn
import torchvision.transforms as transforms
import PIL
import numpy as np
import asyncio


# Broswer control called
# Gamecontroller(model) -> reward
import GameController

# Define model, evolution based approach right now
from create_model import create_model


async def main():
    population = [create_model() for i in range(10)]

    models_per_run = 5

    while True:
        rewards = []
        for model in population:
            instance = GameController()
            reward = instance #??
            rewards.append(reward)

        instances = [GameController() for i in population]
        

        # Sort by rewards
        population = [population[i] for i in np.argsort(rewards)]
        # Keep top models
        population = population[:models_per_run]
        # Save top models
        for i, model in enumerate(population):
            torch.save(model, f"model_{i}.pt")
        
        
        # Mutate models
        for i in range(1, models_per_run):
            population.append(population[i].copy())
            for param in population[-1].parameters():
                param.data += torch.randn_like(param.data) * 0.1

async def main2():
    x = 10
    start_population = [create_model() for i in range(x)]

    # Loop starting games
    population = start_population    
    while True:
        # Loop playing games
        games = [GameController() for i in range(x)]
        nxt_moves = [0 for i in range(x)] # Starting move
        while True:
            instances = [i.getNextFrame(nxt_moves[index]) for index, i in enumerate(games)] # -> [pixels, reward, done] for each instance
            pxl_rw_dn = await asyncio.gather(*instances)
            done = [i[2] for i in pxl_rw_dn]
            if all(done):
                # Games are finished, the loop should break
                # Function?
                break
            # Finding the next move
            nxt_moves = [i.forward(pxl_rw_dn[index][0]) for index, i in enumerate(population)]
            

        # Create new models via mutation and other methods
        # Finding latest rewards?
        rewards = [i[1] for i in pxl_rw_dn]
        # Sort by rewards
        population = [population[i] for i in np.argsort(rewards)]
        # Keep top models
        population = population[:x/2]
        # Save top models
        for i, model in enumerate(population):
            torch.save(model, f"model_{i}.pt")
        
        
        # Mutate models
        for i in range(1, x/2):
            population.append(population[i].copy())
            for param in population[-1].parameters():
                param.data += torch.randn_like(param.data) * 0.1

        # Other methods or smth


asyncio.run(main())
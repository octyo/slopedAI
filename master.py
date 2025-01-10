import torch
import torch.nn as nn
import torchvision.transforms as transforms
import PIL
import numpy as np
import asyncio


# Broswer control called
# Gamecontroller(model) -> reward
from GameController import * 

# Define model, evolution based approach right now
from create_model import create_model


# async def main():
#     population = [create_model() for i in range(10)]

#     models_per_run = 5

#     while True:
#         rewards = []
#         for model in population:
#             instance = GameController()
#             reward = instance #??
#             rewards.append(reward)

#         instances = [GameController() for i in population]
        

#         # Sort by rewards
#         population = [population[i] for i in np.argsort(rewards)]
#         # Keep top models
#         population = population[:models_per_run]
#         # Save top models
#         for i, model in enumerate(population):
#             torch.save(model, f"model_{i}.pt")
        
        
#         # Mutate models
#         for i in range(1, models_per_run):
#             population.append(population[i].copy())
#             for param in population[-1].parameters():
#                 param.data += torch.randn_like(param.data) * 0.1

class GameData:
    def __init__(self, game_object, model):
        self.game_object = game_object
        self.reward = None
        self.next_move = None
        self.latest_frame = None
        self.model = model

async def main():
    x = 10
    # Create starting population
    start_population = [create_model() for i in range(x)]

    population = 0    
    # Loop starting games
    while True:
        if population == 0:
            population = start_population
        games = [GameData(GameController(), population[i]) for i in range(x)]
        for game in games:
            game.next_move = KEYS.NONE

        time.sleep(1)
        lst = [game.game_object.startGame() for game in games]
        await asyncio.gather(*lst)
        lst = [game.game_object.keydown(game.next_move) for game in games]
        await asyncio.gather(*lst)
                
        # Loop playing games
        while True:
            lst = [game.game_object.getNextFrame() for game in games] # -> Only returns frames
            frames = await asyncio.gather(*lst)
            for i, game in enumerate(games):
                game.latest_frame = frames[i]
            # I can access the current state of the game, as well as the time
            done_lst = [game.game_object.currentGameState == GameState.READY for game in games]
            if all(done_lst):
                # Games are finished, the loop should break
                # Function? To note down the times
                break
            # Finding the next move
            for game in games:
                game.next_move = game.model.forward(game.latest_frame)
            
            lst = [game.game_object.keydown(game.next_move) for game in games]
            await asyncio.gather(*lst)
            

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
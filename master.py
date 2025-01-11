import torch
import torch.nn as nn
import torchvision.transforms as transforms
import PIL
import numpy as np
import asyncio


# Broswer control called
# Gamecontroller(model) -> reward
from AsyncGameController import * 

# Define model, evolution based approach right now
from create_model import create_model

def preprocess(image):
    # Crop first
    to_tensor = transforms.Compose([
    transforms.ToTensor()
    ])

    # images = [image1, image2, image3, image4]
    images = image

    sequence = torch.cat([to_tensor(image.convert("L").resize((64,64))) for image in images]).unsqueeze(0)
    return sequence

class GameData:
    def __init__(self, game_object, model):
        self.game_object = game_object
        self.reward = None
        self.next_move = None
        self.latest_frame = None
        self.model = model

async def main():
    x = 4
    # Create starting population
    start_population = [create_model() for i in range(x)]

    population = None
    # Loop starting games
    while True:
        if population == None:
            population = start_population
        games = [GameData(AsyncGameController(id=str(i), url="http://localhost:50317/", debug=True), population[i]) for i in range(x)]
        for game in games:
            game.next_move = KEYS.NONE
        # print("111222")
        # await asyncio.gather(*[game.game_object.long_func(i) for i, game in enumerate(games)])
        
        await asyncio.gather(*[game.game_object.initiate() for game in games])
        # print("222333")
        time.sleep(1)
        lst = [game.game_object.startGame() for game in games]
        await asyncio.gather(*lst)
        lst = [game.game_object.keydown(game.next_move) for game in games]
        await asyncio.gather(*lst)
        
        # Loop playing games
        while True:
            lst = [game.game_object.getNextFrame() for game in games] # -> Only returns frames
            frames = await asyncio.gather(*lst)
            
            
            # I can access the current state of the game, as well as the time
            done_lst = [game.game_object.currentGameState == GameState.READY for game in games]
            if all(done_lst):
                # Games are finished, the loop should break
                # Function? To note down the times
                break

            # Preprocessing
            frames = preprocess(frames)
            print(frames)
            for i, game in enumerate(games):
                game.latest_frame = frames[i]
            # Finding the next move
            for game in games:
                nxt_move = game.model.forward(game.latest_frame) # -> dtype: tensor
                game.next_move = torch.argmax(nxt_move)
                o = KEYS
            time.sleep(0.5)
            lst = [game.game_object.keydown(game.next_move) for game in games]
            await asyncio.gather(*lst)
        

        # Create new models via mutation and other methods
        # Finding latest rewards
        rewards = [game.game_object.getTimeAlive() for game in games]
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
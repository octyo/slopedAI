import torch
import torch.nn as nn
import torchvision.transforms as transforms
import PIL
import numpy as np
import asyncio
import copy


from GameController import * 

# Define model, evolution based approach right now
from create_model import create_model

def preprocess(image):
    # Crop first
    to_tensor = transforms.Compose([transforms.ToTensor()])

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


move_map = {
    0: KEYS.NONE,
    1: KEYS.LEFT,
    2: KEYS.RIGHT,
    3: KEYS.ENTER
}

async def main():
    # Initialize population
    x = 4 # Must be even
    start_population = [create_model() for i in range(x)]    # Create starting population
    population = None
    runs = 0
    # Loop: Runs games
    while True:
        runs += 1
        # The first game played will be with the starting population
        if population == None:
            population = start_population
        
        # Initialize games
        games = [GameData(GameController(id=str(i)+str(0000000)+str(runs), url="http://localhost:55149/", debug=True), population[i]) for i in range(x)]
        
        # Each game will start with NONE as the next move
        for game in games:
            game.next_move = KEYS.NONE

        # New code implementation
        for game in games:
            game.game_object.startGame()
            game.game_object.keydown(game.next_move)

        time.sleep(0.1)

        # Key up
        for game in games:
            game.game_object.keyup(game.next_move)
        
        # Loop: Runs frames in each game
        while True:
            # Get frames from each game
            frames = []
            for game in games:
                frames.append(game.game_object.getNextFrame())
        

            # Access the current state of the game, as well as the time
            done_lst = [game.game_object.currentGameState == GameState.READY for game in games]
            print(done_lst)
            
            # Games are finished, the loop should break
            if all(done_lst):
                print("DONE")
                break

            # print(frames)

            # Preprocessing
            frames = preprocess(frames)
            # print(frames.shape)
            
            # Save to the latest_frame attribute
            for i, game in enumerate(games):
                temp = frames[0][i]
                temp = temp.unsqueeze(0)
                game.latest_frame = temp.unsqueeze(0)

            # Finding the next move
            for game in games:
                # print(game.latest_frame.shape)
                nxt_move = game.model.forward(game.latest_frame) # -> dtype: tensor
                # print(nxt_move)
                pred_idx = torch.argmax(nxt_move, 1)
                # print(game.game_object.id,pred_idx)
                game.next_move = move_map[int(pred_idx)] 
                # KEYS(KEYS(int(pred_idx)).name)
                # print(game.next_move, type(game.next_move))
                print(game.game_object.id, KEYS(int(pred_idx)).name)
                # print("Next_move", game.next_move)

            time.sleep(0.1)
            
            # Send the next move to the game
            for game in games:
                # print(game.next_move)
                game.game_object.keydown(game.next_move)

            await asyncio.sleep(0.1)

            # Key up
            for game in games:
                game.game_object.keyup(game.next_move)

            continue
            lst = [game.game_object.keydown(game.next_move) for game in games]
            await asyncio.gather(*lst)

            lst = [game.game_object.keyup(game.next_move) for game in games]
            await asyncio.gather(*lst)
            
        
        # Create new models via mutation and other methods
        # Finding latest rewards
        rewards = [game.game_object.getTimeAlive() for game in games]
        # Sort by rewards
        population = [population[i] for i in np.argsort(rewards)]
        # Keep top models
        population = population[int(x/2):]
        # Save top models
        for i, model in enumerate(population):
            torch.save(model, f"model_{i}.pt")
        
        
        # Mutate models
        for i in range(0, int(x/2)):
            population.append(copy.deepcopy(population[i]))
            for param in population[-1].parameters():
                param.data += torch.randn_like(param.data) * 0.1

        # Other methods or smth

if __name__ == "__main__":
    asyncio.run(main())


# Old code with async.gather
            # await asyncio.gather(*[game.game_object.initiate() for game in games])
            # time.sleep(1)
            # lst = [game.game_object.startGame() for game in games]
            # await asyncio.gather(*lst)
            # lst = [game.game_object.keydown(game.next_move) for game in games]
            # await asyncio.gather(*lst)

# Old code with async.gather
            # lst = [game.game_object.getNextFrame() for game in games] # -> Only returns frames
            # frames = await asyncio.gather(*lst)
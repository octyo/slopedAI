import torch
import torch.nn as nn
import torchvision.transforms as transforms
import PIL
import numpy as np
import asyncio
import copy
from GameController import * 
from create_model import *
from data import *

class GameData:
    def __init__(self, game_object, model):
        self.game_object = game_object
        self.reward = None
        self.next_move = None
        # self.latest_frame = None
        self.model = model

move_map = {
    0: KEYS.NONE,
    1: KEYS.LEFT,
    2: KEYS.RIGHT,
    3: KEYS.ENTER
}

def CreateGameInstace(instanceIndex, total_hosts):
    # Hosting on four localhost, so open on first then next then next then next, then 
    i = instanceIndex % total_hosts +1 # 1 % 4 = 1, 2 % 4 = 2, 3 % 4 = 3, 4 % 4 = 0

    # return GameController(str(instanceIndex), f"http://localhost:300{i}/", True)
    return GameController(str(instanceIndex), f"http://localhost:8800/", True)

def preprocess(images):
    # to_tensor = transforms.Compose([transforms.ToTensor()])
    # sequence = torch.cat([to_tensor(image.convert("L").resize((64,64))) for image in images]).unsqueeze(0)
    # return sequence
    to_tensor = transforms.Compose([
        transforms.Resize((64,64)),
        transforms.ToTensor()
    ])
    sequence = torch.cat([to_tensor(image.convert("RGB")) for image in images]).unsqueeze(0)
    return sequence

def find_move(model, frame, device):
    # Move frame to the same device as the model
    frame = frame.to(device)
    
    # Perform the forward pass through the model
    output = model.forward(frame)
    
    # Find the index of the maximum predicted value
    pred_idx = torch.argmax(output, dim=1)
    
    # Return the corresponding move from the move map
    return move_map[int(pred_idx)]

def game_player(index, model, total_hosts, random, preset): # Do I need async here?
    model = model.to(torchDevice) # Send to GPU

    try:
        # time.sleep(index/100)
        game = CreateGameInstace(index, total_hosts)  # Initialize game
        game.startGame()
        game.keydown(KEYS.NONE)

        next_move = KEYS.NONE

        while True:
            game.keydown(next_move) # Keydown for next frame

            frame = game.getNextFrame()  # Process frames within the thread
            frame = preprocess([frame])

            # time.sleep(0.5)  # Simulate frame delay
            if game.currentGameState == GameState.READY:
                # return game.getTimeAlive()
                return game.currentTick

            next_move = find_move(model, frame, torchDevice)
            if random == True:
                next_move = KEYS(np.random.randint(0, 3))
            if preset == True:
                next_move = KEYS.NONE

            game.keyup(next_move) # Keyup before next frame. So it remains held if keydown before next frame again
            time.sleep(0.05) # Do not get too fast
    except Exception as e:
        print("Error in game_player")
        return 0

def evolution(models, model_creator):
    find_strategy = np.random.randint(0, 2)
    
    if find_strategy == 0:
        find_model = np.random.randint(0, len(models))
        return gaussian_noise(models[find_model], 0.1, model_creator)
    
    elif find_strategy == 1:
        if len(models) == 1:
            print("Only one model in the population, using gaussian noise instead")
            return gaussian_noise(models[0], 0.1, model_creator)
        
        find_model1 = np.random.randint(0, len(models))
        find_model2 = np.random.randint(0, len(models))

        while find_model1 == find_model2:
            find_model2 = np.random.randint(0, len(models))

        return gaussian_noise(crossover(models[find_model1], models[find_model2], model_creator), 0.1, model_creator)

def read_model(index, model_num):
    return torch.load(f"./data_real_time/model_{model_num}_training/model_{index}.pt")


torchDevice = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
if __name__ == "__main__":
    x = 20
    x_save = 8
    run_count = 0
    total_hosts = 4 # How many hosts are running the game, starting from 3001, then 3002, 3003, 3004 ...
    print(f"Using {torchDevice} for pytorch")
    # Gathering data
    # data_types = ["random_moves", "small_1", "small_2", "small_2_newxsave", "small_1_newxsave", "small_0_newxsave"]
    data_types = ["random_moves", "model_1_training", "model_1_training_evo", "model_2_training", "model_3_training",
                  "model_1_testing", "model_2_testing", "model_3_testing", "preset_moves"
                  ]
    current_data_type = data_types[-1] # data_types[-1]
    model_creator = model_3
    models = [model_creator() for i in range(x)]
    testing = False
    random = False
    preset = True
    model_num = 3

    while True:
        if testing == True:
            models = []
            while len(models) < x:
                try:
                    index = np.random.randint(0, 8) # To choose a random model from the stored
                    print(index) 
                    models.append(read_model(index, model_num))
                    if len(models) == 5:
                        print("Testing, using models, example:", f"data_real_time/model_{model_num}_training/model_{index}.pt")
                except Exception as e:
                    continue

        data = load_data("data_real.json")
        if not current_data_type in list(data.keys()):
            data[current_data_type] = []

        run_count += 1
        time_alive_lst = []

        # Start cleaning process
        process = multiprocessing.Process(target=CleanDeadBrowsers)
        process.start()
        set_high_priority(process.pid)
        
        with ThreadPoolExecutor(max_workers=x) as executor:
            futures = []
            for i in range(x):
                futures.append(executor.submit(game_player, i, models[i], total_hosts, random, preset))
            for future in futures:
                time_alive_lst.append(future.result())
        
        print(time_alive_lst)
        data[current_data_type].append(time_alive_lst) # Save time alive data
        save_data(data, "data_real.json")

        print("Games are done")

        
        if testing == True or preset == True:
            continue

        # Evolutionary strategy
        models = [models[i] for i in np.argsort(time_alive_lst)]
        models = models[-x_save:]
        print("Top models are saved", len(models))
        # Save
        for i, model in enumerate(models):
            torch.save(model, f"data_real_time/model_{i}.pt")
        print("Top models are saved", len(models))
        lst = models
        while len(lst) < x:
            print("Creating new model")
            lst.append(evolution(models, model_creator))
        models = lst   
        
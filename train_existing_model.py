from stable_baselines3 import PPO
import os
from sc2env import Sc2Env
import time
import wandb


LOAD_MODEL = "models/1679495600/5000.zip"

env = Sc2Env()
model = PPO.load(LOAD_MODEL, env=env)

model_name = f"{int(time.time())}"
models_dir = f"models/{model_name}/"
logdir = f"logs/{model_name}/"


conf_dict = {"Model": "Hard Terran",
             "Machine": "DESKTOP",
             "policy": "MlpPolicy",
             "model_save_name": model_name}

run = wandb.init(
    project=f'SC2BOT',
    entity="dams-michal-jakub",
    config=conf_dict,
    sync_tensorboard=True,
    save_code=True,
)


# further train:
TIMESTEPS = 10000
iters = 0
while True:
    print("On iteration: ", iters)
    iters += 1
    model.learn(total_timesteps=TIMESTEPS, reset_num_timesteps=False, tb_log_name=f"PPO")
    model.save(f"{models_dir}/{TIMESTEPS*iters}")

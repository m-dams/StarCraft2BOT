from stable_baselines3 import PPO
import os
from sc2env import Sc2Env
import time
from wandb.integration.sb3 import WandbCallback
import wandb

model_name = f"{int(time.time())}"
models_dir = f"models/{model_name}/"
logdir = f"logs/{model_name}/"


conf_dict = {"Model": "Easy Terran",
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

if not os.path.exists(models_dir):
    os.makedirs(models_dir)

if not os.path.exists(logdir):
    os.makedirs(logdir)

env = Sc2Env()
model = PPO('MlpPolicy', env, verbose=1, tensorboard_log=logdir)

TIMESTEPS = 5000
iters = 0
while True:
    print("On iteration: ", iters)
    iters += 1
    model.learn(total_timesteps=TIMESTEPS, reset_num_timesteps=False, tb_log_name=f"PPO")
    model.save(f"{models_dir}/{TIMESTEPS*iters}")
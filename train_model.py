from stable_baselines3 import PPO
import os
from sc2env import Sc2Env
import time
import wandb

model_name = f"{int(time.time())}"
models_dir = f"models/{model_name}/"
logdir = f"logs/{model_name}/"

conf_dict = {"Model": "Hard Terran",
             "Machine": "DESKTOP",
             "policy": "MlpPolicy",
             "model_save_name": model_name}

# wandb.tensorboard.patch(root_logdir=f"{logdir}/PPO_0")
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
model = PPO('MlpPolicy', env, verbose=1, tensorboard_log=logdir, device="cuda")

TIMESTEPS = 5000
iters = 0
while True:
    print("On iteration: ", iters)
    iters += 1
    model.learn(total_timesteps=TIMESTEPS, reset_num_timesteps=False, tb_log_name=f"PPO")
    model.save(f"{models_dir}/{TIMESTEPS * iters}")
    #  The code is using GPU: you can see this by the allocated memory from GPU by Python process. However,
    # with small batch sizes and potentially small observations, there is not much GPU can do.You need big batches
    # of data to fully utilize GPU.Using device="cpu" might even be faster.potentially small observations, there is
    # not much GPU can do.You need big batches of data to fully utilize GPU.Using device="cpu" might even be faster.

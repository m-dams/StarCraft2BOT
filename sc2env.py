import gym
from gym import spaces
import numpy as np
import subprocess
import pickle
import time
import os


class Sc2Env(gym.Env):
    """Custom Environment that follows gym interface"""

    def __init__(self):
        super(Sc2Env, self).__init__()
        # Define action and observation space
        # They must be gym.spaces objects
        # Example when using discrete actions:
        self.action_space = spaces.Discrete(6)
        self.observation_space = spaces.Box(low=0, high=255,
                                            shape=(168, 184, 3), dtype=np.uint8)
        self.process = None
        self.done = False

    def step(self, action):
        wait_for_action = True
        while wait_for_action:
            try:
                with open('state_rwd_action.pkl', 'rb') as f:
                    state_rwd_action = pickle.load(f)

                    if state_rwd_action['action'] is not None:
                        # print("No action yet")
                        wait_for_action = True
                    else:
                        # print("Needs action")
                        wait_for_action = False
                        state_rwd_action['action'] = action
                        with open('state_rwd_action.pkl', 'wb') as f:
                            pickle.dump(state_rwd_action, f)
            except Exception as e:
                pass

        # waits for the new state to return (map and reward) (no new action yet. )
        wait_for_state = True
        while wait_for_state:
            try:
                if os.path.getsize('state_rwd_action.pkl') > 0:
                    with open('state_rwd_action.pkl', 'rb') as f:
                        state_rwd_action = pickle.load(f)
                        if state_rwd_action['action'] is None:
                            # print("No state yet")
                            wait_for_state = True
                        else:
                            # print("Got state")
                            state = state_rwd_action['state']
                            reward = state_rwd_action['reward']
                            done = state_rwd_action['done']
                            wait_for_state = False

            except Exception as e:
                wait_for_state = True
                map_state = np.zeros((168, 184, 3), dtype=np.uint8)
                # map_state = np.zeros((224, 224, 3), dtype=np.uint8)
                observation = map_state
                # if still failing, input an ACTION, 3 (scout)
                data = {"state": map_state, "reward": 0, "action": 3, "done": False}  # empty action waiting for the next one!
                with open('state_rwd_action.pkl', 'wb') as f:
                    pickle.dump(data, f)

                state = map_state
                reward = 0
                done = False
                action = 3

        info = {}
        observation = state
        return observation, reward, done, info

    def reset(self):
        print("RESETTING ENVIRONMENT...")
        map_state = np.zeros((168, 184, 3), dtype=np.uint8)
        # map_state = np.zeros((224, 224, 3), dtype=np.uint8)
        observation = map_state
        data = {"state": map_state, "reward": 0, "action": None, "done": False}  # empty action waiting for the next one!
        with open('state_rwd_action.pkl', 'wb') as f:
            pickle.dump(data, f)

        # run scripted-bot.py  non-blocking:
        self.process = subprocess.Popen([r"C:\Users\DAMS\PycharmProjects\SC2BOT\venv\Scripts\python.exe", 'scripted_bot.py'])

        return observation  # reward, done, info can't be included

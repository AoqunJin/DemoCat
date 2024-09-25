import numpy as np
from PIL import Image
import gymnasium
from gymnasium.core import Env
from gymnasium.envs.mujoco.mujoco_rendering import MujocoRenderer
from metaworld.envs import ALL_V2_ENVIRONMENTS_GOAL_OBSERVABLE
# import os
# os.environ["MUJOCO_GL"] = "osmesa"

DEFAULT_CAMERA_CONFIG = {
    "distance": 1.25,
    "azimuth": 145,  # rotates the camera around the up vector
    "elevation": -25.0,  # rotates the camera around the right vector
    "lookat": np.array([0.0, 0.65, 0.0]),
    }

DEFAULT_SIZE=512

class CameraWrapper(gymnasium.Wrapper):
    def __init__(self, env: Env, seed:int):
        super().__init__(env)

        self.unwrapped.model.vis.global_.offwidth = DEFAULT_SIZE
        self.unwrapped.model.vis.global_.offheight = DEFAULT_SIZE
        self.unwrapped.mujoco_renderer = MujocoRenderer(env.model, env.data, DEFAULT_CAMERA_CONFIG, DEFAULT_SIZE, DEFAULT_SIZE)

        # Hack: enable random reset
        self.unwrapped._freeze_rand_vec = False
        self.unwrapped.seed(seed)

    def reset(self):
        obs, info = super().reset()
        
        return obs, info

    def step(self, action):
        next_obs, reward, done, truncate, info = self.env.step(action) 
        
        return next_obs, reward, done, truncate, info

def setup_metaworld_env(task_name:str, seed:int):
    env_cls = ALL_V2_ENVIRONMENTS_GOAL_OBSERVABLE[task_name]
    
    env = CameraWrapper(env_cls(render_mode="rgb_array"), seed)
    
    return env


# Test
# env = setup_metaworld_env('button-press-v2-goal-observable', 20)

# obs, _ = env.reset()
# img_array = env.render()
# Image.fromarray(img_array).save('test.png')

# xvfb-run -a python your_script.py
# numpy 1.x
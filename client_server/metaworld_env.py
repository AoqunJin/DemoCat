import copy
from typing import List

import dlimp as dl
import gym
import jax.numpy as jnp
import numpy as np

# need to put https://github.com/tonyzhaozh/act in your PATH for this import to work
import metaworld.envs.mujoco.env_dict as _env_dict
from metaworld_tools import setup_metaworld_env

# EPISODE_LENGTH = 500 * 100

class MetaworldEnv(gym.Env):
    def __init__(
        self,
        env_name: str,
        im_size: int = 256,
        seed: int = 42,
    ):
        self._env_name = env_name
        self._env = setup_metaworld_env(env_name + '-goal-observable')
        # self._env.max_path_length = EPISODE_LENGTH
        self._env._partially_observable = False
        self._env._freeze_rand_vec = False
        self._env._set_task_called = True
        self.observation_space = gym.spaces.Dict(
            {
                "image_primary": gym.spaces.Box(
                    low=np.zeros((im_size, im_size, 3)),
                    high=255 * np.ones((im_size, im_size, 3)),
                    dtype=np.uint8,
                ),
                "proprio": gym.spaces.Box(
                    low=np.ones((7,)) * -1, high=np.ones((7,)), dtype=np.float32
                ),
            }
        )
        self.action_space = gym.spaces.Box(
            low=np.ones((7,)) * -1, high=np.ones((7,)), dtype=np.float32
        )
        # self.camera_names = camera_names
        self._im_size = im_size
        self._rng = np.random.default_rng(seed)

    def step(self, action):
        action = np.concatenate([action[:3], action[6:]], axis=0)
        state, reward, done, truncate, info = self._env.step(action)
        images = self._env.render()
        
        info.update({"state": state})
        obs = {
            "image_primary": images,
            "image_wrist": np.zeros(shape=(128, 128, 3), dtype=np.float32),
            "proprio": np.concatenate(
                [state[:3], np.zeros((3,)), state[3:4]],
                axis=0, dtype=np.float32
            )
        }
        
        if info['success']: 
            self._episode_is_success = 1
            done = True
        if self._env.env.curr_path_length == self._env.env.max_path_length:
            truncate = True
        
        return obs, reward, done, truncate, info
    
    def reset(self, **kwargs):
        state, info = self._env.reset(**kwargs)
        images = self._env.render()
        
        info.update({"state": state})
        obs = {
            "image_primary": images,
            "image_wrist": np.zeros(shape=(128, 128, 3), dtype=np.float32),
            "proprio": np.concatenate(
                [state[:3], np.zeros((3,)), state[3:4]],
                axis=0, dtype=np.float32
            )
        }
        
        return obs, info

    def get_task(self):
        return {
            "language_instruction": [" ".join(self._env_name.split('-')[:-1])],
        }

    def get_episode_metrics(self):
        return {
            "success_rate": self._episode_is_success,
        }


# register gym environments
benchmark = _env_dict.ALL_V2_ENVIRONMENTS
for name in benchmark.keys():
    gym.register(
        name,
        entry_point=lambda: MetaworldEnv(name),
    )

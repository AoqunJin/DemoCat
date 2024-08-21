# file: environments/gym_envs/gym_wrapper.py

import gym
from ..base_env import BaseEnv

class GymEnvWrapper(BaseEnv):
    def __init__(self, env_name):
        self.env = gym.make(env_name, render_mode='rgb_array')
        self.env_name = env_name

    def reset(self):
        return self.env.reset()

    def step(self, action):
        return self.env.step(action)

    def render(self):
        return self.env.render()

    def close(self):
        self.env.close()

    @property
    def action_space(self):
        return self.env.action_space

    @property
    def observation_space(self):
        return self.env.observation_space

# 示例：封装具体的Gym环境
class CartPoleEnv(GymEnvWrapper):
    task_description = ""
    def __init__(self):
        super().__init__('CartPole-v1')

    def reset(self):
        return self.env.reset()[0]

    def step(self, keys):
        if 'Left' in keys:
            action = 0
        else:
            action = 1
        return self.env.step(action), action

class MountainCarEnv(GymEnvWrapper):
    task_description = ""
    def __init__(self):
        super().__init__('MountainCar-v0')

    def reset(self):
        return self.env.reset()[0]
    
    def step(self, keys):
        if 'Left' in keys:
            action = 0
        elif 'Right' in keys:
            action = 1
        else:
            action = 2
        return self.env.step(action), action

class PongEnv(GymEnvWrapper):
    task_description = ""
    def __init__(self):
        super().__init__('pong-v0')

    def reset(self):
        return self.env.reset()[0]
    
    def step(self, keys):
        if 'Up' in keys:
            action = 0
        else:
            action = 1
        return self.env.step(action), action
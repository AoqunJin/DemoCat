import gym
from ..base_env import BaseEnv


class GymEnvWrapper(BaseEnv):
    task_description = "Warning: please rewrite `task_description`."
    default_action = 0
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


class CartPoleEnv(GymEnvWrapper):
    default_action = 0
    def __init__(self):
        super().__init__('CartPole-v1')

    def reset(self):
        return self.env.reset()[0]

    def step(self, keys):
        """
        Step the environment with the given key presses.

        Args:
            keys: A list of strings representing the keys to press.

        Returns:
            A tuple of (observation, reward, done, truncated, info) and the action taken.
        """
        if 'Left' in keys:
            action = 0
        else:
            action = 1
        return self.env.step(action), action


class MountainCarEnv(GymEnvWrapper):
    default_action = 2
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

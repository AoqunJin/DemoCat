# file: environments/base_env.py

from abc import ABC, abstractmethod
import numpy as np

class BaseEnv(ABC):
    @abstractmethod
    def reset(self):
        """重置环境到初始状态，返回初始观察。"""
        pass

    @abstractmethod
    def step(self, action):
        """
        执行一个动作，并返回下一个观察、奖励、是否结束和额外信息。
        
        Args:
            action: 要执行的动作
        
        Returns:
            observation: 执行动作后的观察
            reward: 获得的奖励
            done: 环境是否结束
            info: 额外的信息字典
        """
        pass

    @abstractmethod
    def render(self):
        """渲染环境的当前状态。"""
        pass

    @abstractmethod
    def close(self):
        """关闭环境，释放任何资源。"""
        pass

    @property
    @abstractmethod
    def action_space(self):
        """返回动作空间。"""
        pass

    @property
    @abstractmethod
    def observation_space(self):
        """返回观察空间。"""
        pass
from abc import ABC, abstractmethod


class BaseEnv(ABC):
    @abstractmethod
    def reset(self):
        """Reset the environment to its initial state and returns an initial observation."""
        pass

    @abstractmethod
    def step(self, action):
        """
        Step the environment with the given key presses.

        Args:
            keys: A list of strings representing the keys to press.

        Returns:
            A tuple of (observation, reward, done, truncated, info) and the action taken.
        """
        pass

    @abstractmethod
    def render(self):
        """Render the environment."""
        pass

    @abstractmethod
    def close(self):
        """Close the environment."""
        pass

    @property
    @abstractmethod
    def action_space(self):
        pass

    @property
    @abstractmethod
    def observation_space(self):
        pass

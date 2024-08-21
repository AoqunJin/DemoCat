# file: app/environment.py

from typing import Any
from environments.gym_envs.gym_wrapper import CartPoleEnv, MountainCarEnv, PongEnv
import importlib

class EnvironmentManager:
    def __init__(self):
        self.environments = {}
        self._register_default_environments()

    def _register_default_environments(self):

        self.register_environment('gym')
        self.register_task('gym', 'CartPole', CartPoleEnv)
        self.register_task('gym', 'MountainCar', MountainCarEnv)
        self.register_task('gym', 'Pong', PongEnv)

    def register_environment(self, env_name):
        if env_name in self.environments:
            raise ValueError(f"Environment '{env_name}' is already registered")
        self.environments[env_name] = {}
    
    def register_task(self, env_name, task_name, task_class):
        if env_name not in self.environments:
            raise ValueError(f"Environment '{env_name}' not found")
        self.environments[env_name][task_name] = task_class

    def create_task(self, env_name, task_name):
        if env_name not in self.environments or task_name not in self.environments[env_name]:
            raise ValueError(f"Environment '{env_name}' or task '{task_name}' not found")
        return self.environments[env_name][task_name]()

    def get_available_environments(self):
        return list(self.environments.keys())

    def get_available_tasks(self, env_name):
        return list(self.environments[env_name].keys())

    def load_custom_task(self, env_name, module_path, class_name):
        try:
            module = importlib.import_module(module_path)
            env_class = getattr(module, class_name)
            if env_name not in self.environments:
                self.register_environment(env_name)
            self.register_task(env_name, class_name, env_class)
            return True
        except (ImportError, AttributeError) as e:
            print(f"Error loading custom environment: {e}")
            return False

    def get_task_info(self, env_name, task_name):
        if env_name not in self.environments or task_name not in self.environments[env_name]:
            raise ValueError(f"Environment '{env_name}' or task '{task_name}' not found")

        return self.environments[env_name][task_name].task_description
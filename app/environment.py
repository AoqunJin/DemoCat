import importlib

# Gym
from environments.gym_envs.gym_wrapper import CartPoleEnv, MountainCarEnv
# Real bot
try:
    from environments.real.rm65_env import RM65Cube
    IMPORT_REALMAN = True
except ImportError as e:
    IMPORT_REALMAN = False
# Meta-World
try:
    from environments.metaworld.metaworld_env import (
        Reach, Push, PickPlace, DoorOpen, DrawerOpen, DrawerClose,
        ButtonPressTopdown, PegInsertSide, WindowOpen, WindowClose
    )
    IMPORT_MT = True
except ImportError as e:
    IMPORT_MT = False
# LIBERO
try:
    from environments.libero.libero_env import (
        libero_object_task_0, libero_object_task_1, libero_object_task_2, libero_object_task_3, 
        libero_object_task_4, libero_object_task_5, libero_object_task_6, libero_object_task_7, 
        libero_object_task_8, libero_object_task_9
    )
    IMPORT_LIBERO = True
except ImportError as e:
    IMPORT_LIBERO = False
    print(str(e))

    
class EnvironmentManager:
    def __init__(self):
        self.environments = {}
        self._register_default_environments()

    def _register_default_environments(self):
        if IMPORT_MT:
            self.register_environment('metaworld_mt10')  # metaworld-mt10
            self.register_task('metaworld_mt10', 'reach', Reach)
            self.register_task('metaworld_mt10', 'push', Push)
            self.register_task('metaworld_mt10', 'pick_place', PickPlace)
            self.register_task('metaworld_mt10', 'door_open', DoorOpen)
            self.register_task('metaworld_mt10', 'drawer_open', DrawerOpen)
            self.register_task('metaworld_mt10', 'drawer_close', DrawerClose)
            self.register_task('metaworld_mt10', 'button_press_topdown', ButtonPressTopdown)
            self.register_task('metaworld_mt10', 'peg_insert_side', PegInsertSide)
            self.register_task('metaworld_mt10', 'window_open', WindowOpen)
            self.register_task('metaworld_mt10', 'window_close', WindowClose)
        
        if IMPORT_LIBERO:
            self.register_environment('libero_object')  # libero-object
            self.register_task('libero_object', 'task0', libero_object_task_0)
            self.register_task('libero_object', 'task1', libero_object_task_1)
            self.register_task('libero_object', 'task2', libero_object_task_2)
            self.register_task('libero_object', 'task3', libero_object_task_3)
            self.register_task('libero_object', 'task4', libero_object_task_4)
            self.register_task('libero_object', 'task5', libero_object_task_5)
            self.register_task('libero_object', 'task6', libero_object_task_6)
            self.register_task('libero_object', 'task7', libero_object_task_7)
            self.register_task('libero_object', 'task8', libero_object_task_8)
            self.register_task('libero_object', 'task9', libero_object_task_9)
            
        if IMPORT_REALMAN:
            self.register_environment('real')  # real-65
            self.register_task('real', 'RM65Cube', RM65Cube)
        
        self.register_environment('gym')  # gym-2
        self.register_task('gym', 'CartPole', CartPoleEnv)
        self.register_task('gym', 'MountainCar', MountainCarEnv)

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
import random
import numpy as np
from typing import Any
import cv2
try:
    from .arm import *
except OSError as e:
    print(e)
    
from ..base_env import BaseEnv


def reset_cube_description():
    color = ['red', 'orange', 'yellow', 'green', 'blue', 'purple']
    position = ['top', 'left', 'right', 'front', 'back']
    c = random.sample(color, k=2)
    p = random.choice(position)
    d = f"Task Description:\nTake the {c[0]} cube {p} the {c[1]} cube."
    return d


class RM65(BaseEnv):
    task_description = ""
    default_action = 0
    _instance = None

    def __new__(cls, *args: Any, **kwargs: Any) -> 'RM65':
        if not cls._instance:
            cls._instance = super(RM65, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        if not self._initialized:
            super().__init__()
            self.robot = init()
            self.cap = cv2.VideoCapture(1)
            self._initialized = True
        
    def reset(self):
        init_pose(self.robot)
        return 0
    
    def step(self, keys):
        if 'w' in keys:
            go_forward(self.robot)
            action = 1
        elif 's' in keys:
            go_backward(self.robot)
            action = 2
        elif 'a' in keys:
            go_left(self.robot)
            action = 3
        elif 'd' in keys:
            go_right(self.robot)
            action = 4
        elif 'j' in keys:
            go_down(self.robot)
            action = 5
        elif 'k' in keys:
            go_up(self.robot)
            action = 6
        elif 'l' in keys:
            grasp_close(self.robot)
            action = 7
        elif 'o' in keys:
            grasp_open(self.robot)
            action = 8
        else:
            stop(self.robot)
            action = 0
        
        return (0, 0, False, False, {}), action
    
    def render(self):
        ret, frame = self.cap.read()
        return np.array(frame)
        
    def close(self):
        self.cap.release()

    @property
    def action_space(self):
        return 0

    @property
    def observation_space(self):
        return 0


class RM65Cube(RM65):
    def __init__(self) -> None:
        super().__init__()
    def reset(self):
        self.task_description = reset_cube_description()
        init_pose(self.robot)
        return 0

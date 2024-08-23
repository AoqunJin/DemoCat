import random
import numpy as np
import cv2
import metaworld.envs.mujoco.env_dict as _env_dict
from .arm import *
from ..base_env import BaseEnv

def reset_task_description():
    # TODO 
    return ""

class RM65(BaseEnv):
    task_description = ""
    default_action = 0
    def __init__(self) -> None:
        super().__init__()
        self.robot = init()
        self.cap = cv2.VideoCapture(0)
        
    def reset(self):
        self.robot = init()
        self.task_description = reset_task_description()
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
            action = 0
        
        return (0, 0, False, False, {}), action
    
    def render(self):
        ret, frame = self.cap.read()
        return np.array(frame)
        
    def close(self):
        self.cap.release()
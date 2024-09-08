import random
import numpy as np
from typing import Any
import cv2
from .arm import *
from ..base_env import BaseEnv

DIS_TAB_AND_ARM = """Environment Description:
This is a real-world environment featuring a robotic arm with a gripper attached to its end, a table, and a background wall. The robotic arm is equipped with a black gripper at its end, designed for precise manipulation tasks. The table is made of yellow wood, providing a warm and natural surface for the robotic operations. A white background wall serves as a clean and neutral backdrop to the scene. The setting appears to be a well-lit workspace, likely in a laboratory or industrial setting. Natural shadows are cast by the objects, emphasizing the three-dimensional nature of the setup. This environment represents a typical real-world robotic workspace, showcasing the interaction between advanced robotics and everyday materials."""

def reset_cube_description():
    color = ['red', 'orange', 'yellow', 'green', 'blue', 'purple']
    position = ['top', 'left', 'right', 'front', 'back']
    c = random.sample(color, k=2)
    p = random.choice(position)
    d = f"{DIS_TAB_AND_ARM} In front of the arm, there are cubes of various colors.\n\nTask Description:\nTake the {c[0]} cube {p} the {c[1]} cube."
    return d

def reset_kitchen_description():
    stoves = ["Left Stove", "Right Stove"]  # (左火炉) (右火炉)

    cookware = [
        "Frying Pan",  # (平底锅)
        "Pressure Cooker",  # (高压锅)
        "Pot",  # (锅)
        #"Kettle",  # (水壶)
#"Rice Cooker"  # (电饭煲)
    ]
    ingredients = [
        "Cookware",  # (厨具)
        "Corn",  # (玉米)
        "Eggplant",  # (茄子)
       # "Egg"  # (鸡蛋)
    ]

    cooked_food = [
       # "Hot Dog",  # (热狗)
        "French Fries",  # (薯条)
        "Sandwich",  # (三明治)
        "Beverage"  # (饮料)
    ]

    tableware = [
        "Plate",  # (盘子)
        "Bowl",  # (碗)
        "Spoon"  # (勺子)
    ]
    
    action = random.randint(3, 3)

    if action == 0:
        # 1. Place cookware on the stove
        selected_cookware = random.choice(cookware)
        selected_stove = random.choice(stoves)
        return f"{DIS_TAB_AND_ARM} In front of the arm, there is a small kitchen.\n\nTask Description:\nPlace the {selected_cookware} on the {selected_stove}."
    
    elif action == 1:
        # 2. Put ingredients (raw) into cookware
        selected_ingredient = random.choice(ingredients)
        selected_cookware = random.choice(cookware)
        return f"{DIS_TAB_AND_ARM} In front of the arm, there is a small kitchen.\n\nTask Description:\nPut the {selected_ingredient} into the {selected_cookware}."
    
    elif action == 2:
        # 3. Move cooked food from cookware to tableware (plate, bowl)
        selected_food = random.choice(cooked_food)
        #selected_cookware = random.choice(cookware)    
        selected_tableware = random.choice(tableware)
        return f"{DIS_TAB_AND_ARM} In front of the arm, there is a small kitchen.\n\nTask Description:\nMove the {selected_food} to the {selected_tableware}."
    
    elif action == 3:
        # 4. Arrange tableware
        selected_tableware = random.sample(tableware, k=2)
        positions = ['top', 'left', 'right', 'front', 'back']
        selected_position = random.choice(positions)
        return f"{DIS_TAB_AND_ARM} In front of the arm, there is a small kitchen.\n\nTask Description:\nPlace the {selected_tableware[0]} {selected_position} of the {selected_tableware[1]}."

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
    
class RM65Kitchen(RM65):
    def __init__(self) -> None:
        super().__init__()
    def reset(self):
        self.task_description = reset_kitchen_description()
        init_pose(self.robot)
        return 0
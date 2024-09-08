import random
import numpy as np
import cv2
import metaworld.envs.mujoco.env_dict as _env_dict
from ..base_env import BaseEnv

DIS_TAB_AND_ARM = """Environment Description:
This is a computer-generated simulated environment featuring a robotic arm with a gripper attached to its end, a table, and several objects in the environment. The robotic arm is red, and the two fingers of the gripper are white and blue respectively. The table is made of brown wood, with gray vertical barriers added to its edges. There are shadows for all objects in the environment. The simulated environment looks very realistic and adheres to physical laws."""

def move_up_and_left_right():
    if random.random() < 1/3:
        return "", ""
    left_right = ["left", "right"]
    random.shuffle(left_right)
    return f" and to the {left_right[0]}", f" and to the {left_right[1]}"
    
def move_forward_and_up_left_right():
    if random.random() < 1/4:
        return "", ""
    left_right = ["left", "right"]
    random.shuffle(left_right)
    left_right_up_down = random.choice([left_right, ["up", "down"]])
    return f" and to the {left_right_up_down[0]}", f" and to the {left_right_up_down[1]}"
    
def gripper_closes():
    if random.random() < 1/2:
        return ""
    return " The gripper then closes."

class MetaWorldWrapper(BaseEnv):
    task_description = "Warning: please rewrite `task_description`."
    default_action = np.array([0, 0, 0, 0])
    def __init__(self, env_name):
        self.env = _env_dict.ALL_V2_ENVIRONMENTS[env_name]()
        self.env_name = env_name
        self.env._partially_observable = False
        self.env._freeze_rand_vec = False
        self.env._set_task_called = True
        
    def reset(self):
        return self.env.reset()

    def step(self, keys):
        action = np.array([0, 0, 0, 0])
        if 'w' in keys: action[1] += 1
        elif 's' in keys: action[1] -= 1
        if 'a' in keys: action[0] += 1
        elif 'd' in keys: action[0] -= 1
        if 'j' in keys: action[2] -= 1
        elif 'k' in keys: action[2] += 1
        if 'l' in keys: action[3] += 1
        elif 'o' in keys: action[3] -= 1
            
        obs, rew, done, info = self.env.step(action)
        
        truncated = (self.env.curr_path_length == self.env.max_path_length)
        done = info['success']
        
        return (obs, rew, done, truncated, info), action

    def render(self):
        camera_name="corner"  # ["behindGripper", "corner", ...]
        img = self.env.sim.render(*(224, 224), mode="offscreen", camera_name=camera_name)[:,:,::-1]
        if camera_name in ["behindGripper"]: img = cv2.rotate(img, cv2.ROTATE_180)
        return img

    def close(self):
        self.env.close()

    @property
    def action_space(self):
        return self.env.action_space

    @property
    def observation_space(self):
        return self.env.observation_space

class Instruct(MetaWorldWrapper):
    def __init__(self):
        super().__init__("reach-v2")
    def reset(self):
        task_description = self.generate_sequence()
        self.task_description = f"{DIS_TAB_AND_ARM} There is a red cylinder on the table.\n\nTask Description:\n{task_description}"
        return super().reset()
    def step(self, keys):
        (obs, rew, done, truncated, info), action = super().step(keys)
        done = False
        return (obs, rew, done, truncated, info), action
    
    def generate_subsequence(self):
        x = random.choice(['Ahead', 'Behind'])
        y = random.choice(['Left', 'Right'])
        z = random.choice(['Up', 'Down'])
        return " and ".join(random.sample([x, y, z], k=random.randint(1, 3)))
    
    def generate_sequence(self):
        seq_l = random.randint(1, 3)
        seq = ["Go " + self.generate_subsequence() for i in range(seq_l)]
        if random.random() < 1/6:
            color = random.choice([" Red", ""])
            seq[random.choice([0, -1])] = f'Grip{color} Cylinder'
        if random.random() < 1/6:
            color = random.choice([" Red", ""])
            point_dot = random.choice(["point", "dot"])
            seq[random.choice([0, -1])] = f'Go{color} {point_dot}'
        
        seq = [f"{i+1}. " + s + "." for i, s in enumerate(seq)]
        
        return "\n".join(seq)

class ButtonPressTopdown(MetaWorldWrapper):
    def __init__(self):
        super().__init__("button-press-topdown-v2")
        left_right = move_up_and_left_right()
        self.task_description = [
            f"The arm moves upward{left_right[0]}, reaching a position level with the button. Then it moves upward{left_right[1]}, reaching a position higher than the button. Next, it moves forward, positioning itself above the button.{gripper_closes()} And finally, the arm moves downward to press the button.",
            f"The arm moves upward{left_right[0]}, Then it moves upward{left_right[1]}, reaching a position higher than the button. Next, it moves forward, positioning itself above the button.{gripper_closes()} And finally, the arm moves downward to press the button.",
            f"The arm moves upward, reaching a position higher than the button. Next, it moves forward, positioning itself above the button.{gripper_closes()} And finally, the arm moves downward to press the button.",
        ]
    def reset(self):
        task_description = random.choice(self.task_description)
        self.task_description = f"{DIS_TAB_AND_ARM} In front of the arm, there is a button vertically connected to a device, which is placed vertically on the table surface. The bottom of the button is black, and the top is red. The bottom of the device is black, and the top is yellow.\n\nTask Description:\n{task_description}"
        return super().reset()

class ButtonPressTopdownWall(MetaWorldWrapper):
    def __init__(self):
        super().__init__("button-press-topdown-wall-v2")
        left_right = move_up_and_left_right()
        self.task_description = [
            f"The arm moves upward{left_right[0]}, reaching a position level with the button. Then it moves upward{left_right[1]}, reaching a position higher than the button. Next, it moves forward, crossing over the wall and positioning itself above the button.{gripper_closes()} And finally, the arm moves downward to press the button.",
            f"The arm moves upward{left_right[0]}, Then it moves upward{left_right[1]}, reaching a position higher than the button. Next, it moves forward, crossing over the wall and positioning itself above the button.{gripper_closes()} And finally, the arm moves downward to press the button.",
            f"The arm moves upward, reaching a position higher than the button. Next, it moves forward, crossing over the wall and positioning itself above the button.{gripper_closes()} And finally, the arm moves downward to press the button.",
        ]
    def reset(self):
        task_description = random.choice(self.task_description)
        self.task_description = f"{DIS_TAB_AND_ARM} In front of the arm, there is a button vertically connected to a device, which is placed vertically on the table surface. The bottom of the button is black, and the top is red. The bottom of the device is black, and the top is yellow. Near the device, there is a wall, which is reddish-brown in color.\n\nTask Description:\n{task_description}"
        return super().reset()

class ButtonPress(MetaWorldWrapper):
    def __init__(self):
        super().__init__("button-press-v2")
        left_right_up_down = move_forward_and_up_left_right()
        self.task_description = [
            f"The arm moves downward and to the forward to a horizontal position directly facing the button. Next, it moves forward{left_right_up_down[0]}, then moves forward{left_right_up_down[1]} to press the button.",
            f"The arm moves downward to a horizontal position directly facing the button. Next, it moves forward{left_right_up_down[0]}, then moves forward{left_right_up_down[1]} to press the button.",
            f"The arm moves downward and to the forward to a horizontal position directly facing the button. Next, it moves forward to press the button.",
            f"The arm moves downward to a horizontal position directly facing the button. Next, it moves forward to press the button.",
        ]
    def reset(self):
        task_description = random.choice(self.task_description)
        ly = random.choice(["horizontally", "lying down"])
        self.task_description = f"{DIS_TAB_AND_ARM} In front of the arm, there is a button horizontally connected to a device, which is also placed {ly} on the table surface, facing the arm directly. The bottom of the button is black, and the top is red. The bottom of the device is black, and the top is yellow.\n\nTask Description:\n{task_description}"
        return super().reset()    
     
class ButtonPressWall(MetaWorldWrapper):
    def __init__(self):
        super().__init__("button-press-wall-v2")
        left_right_up_down = move_forward_and_up_left_right()
        self.task_description = [
            f"The arm moves downward and to the forward to a horizontal position directly facing the button. Next, it moves forward{left_right_up_down[0]}, crossing over the wall.{gripper_closes()} Then moves forward{left_right_up_down[1]} to press the button.",
            f"The arm moves downward to a horizontal position directly facing the button. Next, it moves forward{left_right_up_down[0]}, crossing over the wall.{gripper_closes()} Then moves forward{left_right_up_down[1]} to press the button.",
        ]
    def reset(self):
        task_description = random.choice(self.task_description)
        ly = random.choice(["horizontally", "lying down"])
        self.task_description = f"{DIS_TAB_AND_ARM} In front of the arm, there is a button horizontally connected to a device, which is also placed {ly} on the table surface, facing the arm directly. The bottom of the button is black, and the top is red. The bottom of the device is black, and the top is yellow. Near the device, there is a wall, which is reddish-brown in color.\n\nTask Description:\n{task_description}"
        return super().reset()
        
class CoffeeButton(MetaWorldWrapper):
    def __init__(self):
        super().__init__('coffee-button-v2')
        cross_cup = random.choice(["crossing over the cup, ", ""])
        self.task_description = [
            f"The arm moves upward to a horizontal position directly facing the button, then the arm moves forward, {cross_cup}and press the button.",
            f"The arm moves forward {cross_cup}and press the button.",
        ]
    def reset(self):
        task_description = random.choice(self.task_description)
        self.task_description = f"{DIS_TAB_AND_ARM} In front of the arm, there is a coffee machine placed vertically on the table surface. It has a button directly in front, facing the arm. Between the coffee machine and the arm, there is a cup. The coffee machine is red, with a black base and handle. The button on it is white, and the cup is white.\n\nTask Description:\n{task_description}"
        return super().reset()
        
class CoffeePull(MetaWorldWrapper):
    def __init__(self):
        super().__init__('coffee-pull-v2')
        point_dot = random.choice(["point", "dot"])
        self.task_description = [
            f"The arm moves upward to a horizontal position directly facing the button, then the arm moves forward press the button and to a position above the cup. Next, it moves downward and then grasps the cup. Finally, it moves backward, dragging the cup to the green {point_dot}.",
            f"The arm moves forward press the button and to a position above the cup. Next, it moves downward and then grasps the cup. Finally, it moves backward, dragging the cup to the green {point_dot}.",
            f"The arm moves upward to a horizontal position directly facing the button, then the arm moves forward to a position above the cup. Next, it moves downward and then grasps the cup. Finally, it moves backward, dragging the cup to the green {point_dot}.",
            f"The arm moves forward to a position above the cup. Next, it moves downward and then grasps the cup. Finally, it moves backward, dragging the cup to the green {point_dot}.",
        ]
    def reset(self):
        task_description = random.choice(self.task_description)
        self.task_description = f"{DIS_TAB_AND_ARM} In front of the arm, there is a coffee machine placed vertically on the table surface. It has a button directly in front, facing the arm. Between the coffee machine and the arm, there is a cup. The coffee machine is red, with a black base and handle. The button on it is white, and the cup is white.\n\nTask Description:\n{task_description}"
        return super().reset()

class CoffeePush(MetaWorldWrapper):
    def __init__(self):
        super().__init__('coffee-push-v2')
        point_dot = random.choice(["point", "dot"])
        self.task_description = [
            f"The arm moves upward to a horizontal position directly facing the button, then the arm moves forward to a position above the cup. Next, it moves downward and then grasps the cup. Finally, it moves forward, pushing the cup to the red {point_dot}.",
            f"The arm moves forward to a position above the cup. Next, it moves downward and then grasps the cup. Finally, it moves forward, pushing the cup to the red {point_dot}.",
        ]
    def reset(self):
        task_description = random.choice(self.task_description)
        self.task_description = f"{DIS_TAB_AND_ARM} In front of the arm, there is a coffee machine placed vertically on the table surface. It has a button directly in front, facing the arm. Between the coffee machine and the arm, there is a cup. The coffee machine is red, with a black base and handle. The button on it is white, and the cup is white.\n\nTask Description:\n{task_description}"
        return super().reset()
        
class PlateSlide(MetaWorldWrapper):
    def __init__(self):
        super().__init__('plate-slide-v2')
        left_right = move_up_and_left_right()
        point_dot = random.choice(["point", "dot"])
        self.task_description = [
            f"The arm moves upwards{left_right[0]}.{gripper_closes()} Then moves down{left_right[1]} to press the disc, and finally moves forward to push the disc to the red {point_dot}.",
            f"The gripper closes. Then moves down to press the disc, and finally moves forward to push the disc to the red {point_dot}.",
            f"The arm moves down to press the disc, and finally moves forward to push the disc to the red {point_dot}.",
        ]
    def reset(self):
        task_description = random.choice(self.task_description)
        self.task_description = f"{DIS_TAB_AND_ARM} There is a soccer goal vertically placed on the table in front of the arm, directly facing it. There is a disc under the arm. The goal is red with a white net, and the disc is black.\n\nTask Description:\n{task_description}"
        return super().reset()

class PlateSlideBack(MetaWorldWrapper):
    def __init__(self):
        super().__init__('plate-slide-back-v2')
        point_dot = random.choice(["point", "dot"])
        self.task_description = [
            f"The arm moves forward.{gripper_closes()} Then moves down forward and down to press the disc, and finally moves backward to pull the disc to the red {point_dot}.",
            f"The gripper closes. Then moves down forward and down to press the disc, and finally moves backward to pull the disc to the red {point_dot}.",
            f"The arm moves down forward and down to press the disc, and then moves backward to pull the disc to the red {point_dot}.",
        ]
    def reset(self):
        task_description = random.choice(self.task_description)
        self.task_description = f"{DIS_TAB_AND_ARM} There is a soccer goal vertically placed on the table in front of the arm, directly facing it. There is a disc in the middle of the goal. The goal is red with a white net, and the disc is black.\n\nTask Description:\n{task_description}"
        return super().reset()
        
class PlateSlideSide(MetaWorldWrapper):
    def __init__(self):
        super().__init__('plate-slide-side-v2')
        left_right = move_up_and_left_right()
        point_dot = random.choice(["point", "dot"])
        self.task_description = [            
            f"The arm moves upwards{left_right[0]}.{gripper_closes()} Then moves down{left_right[1]} to press the disc, and finally moves right to push the disc to the red {point_dot}.",
            f"The gripper closes. Then moves down to press the disc, and finally moves right to push the disc to the red {point_dot}.",
            f"The arm moves down to press the disc, and finally moves right to push the disc to the red {point_dot}.",
        ]
    def reset(self):
        task_description = random.choice(self.task_description)
        self.task_description = f"{DIS_TAB_AND_ARM} There is a soccer goal vertically placed on the table in front of the arm, at the right front of the arm. There is a disc under the goal. The goal is red with a white net, and the disc is black.\n\nTask Description:\n{task_description}"
        return super().reset()

class PlateSlideBackSide(MetaWorldWrapper):
    def __init__(self):
        super().__init__('plate-slide-back-side-v2')
        point_dot = random.choice(["point", "dot"])
        self.task_description = [
            f"The arm moves right.{gripper_closes()} Then moves down right and down to press the disc, and finally moves left to pull the disc to the red {point_dot}.",
            f"The gripper closes. Then moves down right and down to press the disc, and finally moves left to pull the disc to the red {point_dot}.",
            f"The arm moves down right and down to press the disc, and then moves left to pull the disc to the red {point_dot}.",
        ]
    def reset(self):
        task_description = random.choice(self.task_description)
        self.task_description = f"{DIS_TAB_AND_ARM} There is a soccer goal vertically placed on the table in front of the arm, at the right front of the arm. There is a disc in front of the goal. The goal is red with a white net, and the disc is black.\n\nTask Description:\n{task_description}"
        return super().reset()
        
class FaucetOpen(MetaWorldWrapper):
    def __init__(self):
        super().__init__('faucet-open-v2')
        pos = random.sample(["", "The arm moves downward to a horizontal position directly facing the faucet. "], k=2)
        self.task_description = [
            f"{pos[0]}The arm moves forward and to the right, reaching the right side of the faucet.{gripper_closes()} {pos[1]}Next, it moves to the left, turning the faucet towards the left side."
        ]
    def reset(self):
        task_description = random.choice(self.task_description)
        self.task_description = f"{DIS_TAB_AND_ARM} In front of the arm, there is a faucet placed vertically on the table surface. The upper half of the faucet is red, and the lower half is gray.\n\nTask Description:\n{task_description}"
        return super().reset()

class FaucetClose(MetaWorldWrapper):
    def __init__(self):
        super().__init__('faucet-close-v2')
        pos = random.sample(["", "The arm moves downward to a horizontal position directly facing the faucet. "], k=2)
        self.task_description = [
            f"{pos[0]}The arm moves forward and to the left, reaching the left side of the faucet.{gripper_closes()} {pos[1]}Next, it moves to the right, turning the faucet towards the right side."
        ]
    def reset(self):
        task_description = random.choice(self.task_description)
        self.task_description = f"{DIS_TAB_AND_ARM} In front of the arm, there is a faucet placed vertically on the table surface. The upper half of the faucet is red, and the lower half is gray.\n\nTask Description:\n{task_description}"
        return super().reset()

class PickPlaceWall(MetaWorldWrapper):
    def __init__(self):
        super().__init__('pick-place-wall-v2')
        point_dot = random.choice(["point", "dot"])
        color = random.choice(["", " blue"])
        self.task_description = [
            f"1. Grip Red Cylinder.\n2. Go{color} {point_dot}."
        ]
    def reset(self):
        task_description = random.choice(self.task_description)
        self.task_description = f"{DIS_TAB_AND_ARM} There is a red cylinder on the table. Near the cylinder, there is a wall, which is reddish-brown in color.\n\nTask Description:\n{task_description}"
        return super().reset()

class PickPlace(MetaWorldWrapper):
    def __init__(self):
        super().__init__('pick-place-v2')
        point_dot = random.choice(["point", "dot"])
        color = random.choice(["", " blue"])
        self.task_description = [
            f"1. Grip Red Cylinder.\n2. Go{color} {point_dot}."
        ]
    def reset(self):
        task_description = random.choice(self.task_description)
        self.task_description = f"{DIS_TAB_AND_ARM} There is a red cylinder on the table.\n\nTask Description:\n{task_description}"
        return super().reset()

class Push(MetaWorldWrapper):
    def __init__(self):
        super().__init__('push-v2')
        point_dot = random.choice(["point", "dot"])
        color = random.choice(["", " green"])
        self.task_description = [
            f"1. Grip Red Cylinder.\n2. Go{color} {point_dot}."
        ]
    def reset(self):
        task_description = random.choice(self.task_description)
        self.task_description = f"{DIS_TAB_AND_ARM} There is a red cylinder on the table.\n\nTask Description:\n{task_description}"
        return super().reset()

class PushWall(MetaWorldWrapper):
    def __init__(self):
        super().__init__('push-wall-v2')
        point_dot = random.choice(["point", "dot"])
        color = random.choice(["", " green"])
        self.task_description = [
            f"1. Grip Red Cylinder.\n2. Go{color} {point_dot}."
        ]
    def reset(self):
        task_description = random.choice(self.task_description)
        self.task_description = f"{DIS_TAB_AND_ARM} There is a red cylinder on the table. Near the cylinder, there is a wall, which is reddish-brown in color.\n\nTask Description:\n{task_description}"
        return super().reset()
     
class PushBack(MetaWorldWrapper):
    def __init__(self):
        super().__init__('push-back-v2')
        point_dot = random.choice(["point", "dot"])
        color = random.choice(["", " green"])
        self.task_description = [
            f"1. Grip brown cube.\n2. Go{color} {point_dot}."
        ]
    def reset(self):
        task_description = random.choice(self.task_description)
        self.task_description = f"{DIS_TAB_AND_ARM} There is a brown cube on the table.\n\nTask Description:\n{task_description}"
        return super().reset()
        
# class SweepIntoGoal(MetaWorldWrapper):
#     def __init__(self):
#         super().__init__('sweep-into-v2')
#     def reset(self):
#         self.task_description = f"{DIS_TAB_AND_ARM} "
#         return super().reset()

class Sweep(MetaWorldWrapper):
    def __init__(self):
        super().__init__('sweep-v2')
        point_dot = random.choice(["point", "dot"])
        little = random.choice(["", " little"])
        self.task_description = [
            f"1. Grip brown cube.\n2. Go purple{little} {point_dot}."
        ]
    def reset(self):
        task_description = random.choice(self.task_description)
        self.task_description = f"{DIS_TAB_AND_ARM} There is a brown cube on the table.\n\nTask Description:\n{task_description}"
        return super().reset()

# class Reach(MetaWorldWrapper):
#     def __init__(self):
#         super().__init__('reach-v2')
#     def reset(self):
#         self.task_description = f"{DIS_TAB_AND_ARM} "
#         return super().reset()

class ReachWall(MetaWorldWrapper):
    def __init__(self):
        super().__init__('reach-wall-v2')
        point_dot = random.choice(["point", "dot"])
        color = random.choice(["", " red"])
        self.task_description = [
            f"1. Grip Red Cylinder.\n2. Go{color} {point_dot}.",
            f"1. Go{color} {point_dot}.",
        ]
    def reset(self):
        task_description = random.choice(self.task_description)
        self.task_description = f"{DIS_TAB_AND_ARM} There is a red cylinder on the table. Near the cylinder, there is a wall, which is reddish-brown in color.\n\nTask Description:\n{task_description}"
        return super().reset()
    
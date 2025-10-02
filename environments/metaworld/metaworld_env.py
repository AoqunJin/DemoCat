import sys
import numpy as np
import metaworld
import gymnasium as gym
from gymnasium.envs.mujoco import MujocoRenderer
from ..base_env import BaseEnv


class MetaWorldEnv(BaseEnv):
    task_description = "Warning: please rewrite `task_description`."
    default_action = np.array([0, 0, 0, 0])
    def __init__(self, env_name, instruction):
        self.task_description = instruction
        self.env_name = env_name
        self.env = gym.make('Meta-World/MT1', env_name=env_name, 
                            width=256, height=256, render_mode="rgb_array", 
                            camera_name="corner")
        self.env.unwrapped.model.cam_pos[2][:]=[0.75, 0.075, 0.7]

        model, data = self.env.unwrapped.model, self.env.unwrapped.data
        self.hand_renderer = MujocoRenderer(model, data, None, 256, 256, 1000, None, "behindGripper")

    def reset(self):
        return self.env.reset()[0]

    def step(self, keys):
        action = np.array([0, 0, 0, 0])
        if 'w' in keys: action[1] += 1
        elif 's' in keys: action[1] -= 1
        if 'a' in keys: action[0] -= 1
        elif 'd' in keys: action[0] += 1
        if 'j' in keys: action[2] -= 1
        elif 'k' in keys: action[2] += 1
        if 'l' in keys: action[3] += 1
        elif 'o' in keys: action[3] -= 1
            
        obs, rew, done, truncated, info = self.env.step(action)
        done = info['success'] or done
        
        return (obs, rew, done, truncated, info), action

    # def render(self):
    #     return np.array(self.env.render())[::-1, ::-1, ::-1]

    def render(self):
        return {"obs_agent": np.array(self.env.render())[::-1, ::-1, ::-1],
                "obs_griper": np.array(self.hand_renderer.render("rgb_array"))[:, :, ::-1]}

    def close(self):
        self.env.close()

    @property
    def action_space(self):
        return self.env.action_space

    @property
    def observation_space(self):
        return self.env.observation_space


def create_task_class(task_key, instruction):
    class_name = ''.join(word.capitalize() for word in task_key.replace('-v3', '').split('-'))

    def __init__(self):
        MetaWorldEnv.__init__(self, task_key, instruction)

    new_class = type(
        class_name,
        (MetaWorldEnv,),
        {
            '__init__': __init__,
            '__doc__': f"MetaWorld task: {instruction}"
        }
    )
    return new_class


MT_TASK_MAP = {
    "assembly-v3": "pick up a nut and place it onto a peg",
    "basketball-v3": "dunk the basketball into the basket",
    "bin-picking-v3": "grasp the puck from one bin and place it into another bin",
    "box-close-v3": "grasp the cover and close the box with it",
    "button-press-topdown-v3": "press a button from the top",
    "button-press-topdown-wall-v3": "bypass a wall and press a button from the top",
    "button-press-v3": "press a button",
    "button-press-wall-v3": "bypass a wall and press a button",
    "coffee-button-v3": "push a button on the coffee machine",
    "coffee-pull-v3": "pull a mug from a coffee machine",
    "coffee-push-v3": "push a mug under a coffee machine",
    "dial-turn-v3": "rotate a dial 180 degrees",
    "disassemble-v3": "pick a nut out of the a peg",
    "door-close-v3": "close a door with a revolving joint",
    "door-lock-v3": "lock the door by rotating the lock clockwise",
    "door-open-v3": "open a door with a revolving joint",
    "door-unlock-v3": "unlock the door by rotating the lock counter-clockwise",
    "hand-insert-v3": "insert the gripper into a hole",
    "drawer-close-v3": "push and close a drawer",
    "drawer-open-v3": "open a drawer",
    "faucet-open-v3": "rotate the faucet counter-clockwise",
    "faucet-close-v3": "rotate the faucet clockwise",
    "hammer-v3": "hammer a screw on the wall",
    "handle-press-side-v3": "press a handle down sideways",
    "handle-press-v3": "press a handle down",
    "handle-pull-side-v3": "pull a handle up sideways",
    "handle-pull-v3": "pull a handle up",
    "lever-pull-v3": "pull a lever down 90 degrees",
    "pick-place-wall-v3": "pick a puck, bypass a wall and place the puck",
    "pick-out-of-hole-v3": "pick up a puck from a hole",
    "pick-place-v3": "pick and place a puck to a goal",
    "plate-slide-v3": "slide a plate into a cabinet",
    "plate-slide-side-v3": "slide a plate into a cabinet sideways",
    "plate-slide-back-v3": "get a plate from the cabinet",
    "plate-slide-back-side-v3": "get a plate from the cabinet sideways",
    "peg-insert-side-v3": "insert a peg sideways",
    "peg-unplug-side-v3": "unplug a peg sideways",
    "soccer-v3": "kick a soccer into the goal",
    "stick-push-v3": "grasp a stick and push a box using the stick",
    "stick-pull-v3": "grasp a stick and pull a box with the stick",
    "push-v3": "push the puck to a goal",
    "push-wall-v3": "bypass a wall and push a puck to a goal",
    "push-back-v3": "push a puck to a goal",
    "reach-v3": "reach a goal position",
    "reach-wall-v3": "bypass a wall and reach a goal",
    "shelf-place-v3": "pick and place a puck onto a shelf",
    "sweep-into-v3": "sweep a puck into a hole",
    "sweep-v3": "sweep a puck off the table",
    "window-open-v3": "push and open a window",
    "window-close-v3": "push and close a window",
}


current_module = sys.modules[__name__]

_classes = {}
for task_key, instruction in MT_TASK_MAP.items():
    cls = create_task_class(task_key, "Task Description: " + instruction)
    _classes[cls.__name__] = cls
    setattr(current_module, cls.__name__, cls)

__all__ = list(_classes.keys())

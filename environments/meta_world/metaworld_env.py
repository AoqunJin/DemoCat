import random
import numpy as np
import metaworld.envs.mujoco.env_dict as _env_dict
from ..base_env import BaseEnv

class MetaWorldWrapper(BaseEnv):
    task_description = ""
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
        if 'g' in keys: action[3] += 1
        elif 'h' in keys: action[3] -= 1
            
        obs, rew, done, info = self.env.step(action)
        
        truncated = (self.env.curr_path_length == self.env.max_path_length)
        done = info['success']
        
        return (obs, rew, done, truncated, info), action

    def render(self):
        return self.env.sim.render(*(224, 224), mode="offscreen", camera_name="corner")[:,:,::-1]

    def close(self):
        self.env.close()

    @property
    def action_space(self):
        return self.env.action_space

    @property
    def observation_space(self):
        return self.env.observation_space

def generate_subsequence():
    x = random.choice(['Ahead', 'Behind'])
    y = random.choice(['Left', 'Right'])
    z = random.choice(['Up', 'Down'])
    
    return " and ".join(random.sample([x, y, z], k=random.randint(1, 3)))

def generate_sequence():
    seq_l = random.randint(1, 3)
    seq = ["Go " + generate_subsequence() for i in range(seq_l)]
    
    if random.random() < 1/6:
        seq[random.choice([0, -1])] = 'Grip Cube'
    
    seq = [f"{i+1}. " + s for i, s in enumerate(seq)]
    
    return "\n".join(seq)

class Instruct(MetaWorldWrapper):
    def __init__(self):
        super().__init__("reach-v2")
    def reset(self):
        self.task_description = generate_sequence()
        return super().reset()

class ButtonPressTopdown(MetaWorldWrapper):
    def __init__(self):
        super().__init__("button-press-topdown-v2")
    def step(self, keys):
        return super().step(keys)
        
class ButtonPressTopdownWall(MetaWorldWrapper):
    def __init__(self):
        super().__init__("button-press-topdown-wall-v2")
        
class ButtonPress(MetaWorldWrapper):
    def __init__(self):
        super().__init__("button-press-v2")
        
class ButtonPressWall(MetaWorldWrapper):
    def __init__(self):
        super().__init__("button-press-wall-v2")

class CoffeeButton(MetaWorldWrapper):
    def __init__(self):
        super().__init__('coffee-button-v2')
    
class CoffeePull(MetaWorldWrapper):
    def __init__(self):
        super().__init__('coffee-pull-v2')
    
class CoffeePush(MetaWorldWrapper):
    def __init__(self):
        super().__init__('coffee-push-v2')

class PlateSlide(MetaWorldWrapper):
    def __init__(self):
        super().__init__('plate-slide-v2')
    
class PlateSlideSide(MetaWorldWrapper):
    def __init__(self):
        super().__init__('plate-slide-side-v2')
    
class PlateSlideBack(MetaWorldWrapper):
    def __init__(self):
        super().__init__('plate-slide-back-v2')
    
class PlateSlideBackSide(MetaWorldWrapper):
    def __init__(self):
        super().__init__('plate-slide-back-side-v2')  
    
class FaucetOpen(MetaWorldWrapper):
    def __init__(self):
        super().__init__('faucet-open-v2')
    
class FaucetClose(MetaWorldWrapper):
    def __init__(self):
        super().__init__('faucet-close-v2')

class HandInsert(MetaWorldWrapper):
    def __init__(self):
        super().__init__('hand-insert-v2')

class PickOutOfHole(MetaWorldWrapper):
    def __init__(self):
        super().__init__('pick-out-of-hole-v2')
    
class PickPlaceWall(MetaWorldWrapper):
    def __init__(self):
        super().__init__('pick-place-wall-v2')

class PickPlace(MetaWorldWrapper):
    def __init__(self):
        super().__init__('pick-place-v2')

class Push(MetaWorldWrapper):
    def __init__(self):
        super().__init__('push-v2')
    
class PushWall(MetaWorldWrapper):
    def __init__(self):
        super().__init__('push-wall-v2')

class PushBack(MetaWorldWrapper):
    def __init__(self):
        super().__init__('push-back-v2')

class SweepIntoGoal(MetaWorldWrapper):
    def __init__(self):
        super().__init__('sweep-into-v2')
    
class Sweep(MetaWorldWrapper):
    def __init__(self):
        super().__init__('sweep-v2')

class Reach(MetaWorldWrapper):
    def __init__(self):
        super().__init__('reach-v2')
    
class ReachWall(MetaWorldWrapper):
    def __init__(self):
        super().__init__('reach-wall-v2')
        

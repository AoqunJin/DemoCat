from typing import Dict
import numpy as np


def key_to_action(keys, rules: Dict = {"w": "FROMT", "s": "BACK", "a": "LEFT", "d": "RIGHT", "j": "DOWN", "k": "UP", "l": "CLOSE", "o": "OPEN"}):    
    action = None
    for k in keys:
        act = rules.get(k, None)
        if act is not None:
            if action is None: action = np.array([0, 0, 0, 0, 0, 0, 0])
            if act == "FROMT": action[1] += 1
            if act == "BACK": action[1] -= 1
            if act == "LEFT": action[0] -= 1
            if act == "RIGHT": action[0] += 1
            if act == "DOWN": action[2] -= 1
            if act == "UP": action[2] += 1
            if act == "CLOSE": action[6] += 1
            if act == "OPEN": action[6] -= 1
    
    return action
            
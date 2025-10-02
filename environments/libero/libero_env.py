import os
import random
import math
import numpy as np
from libero.libero import benchmark
from libero.libero.envs import OffScreenRenderEnv
from libero.libero import get_libero_path
import gym
from ..base_env import BaseEnv


def quat2axisangle(quat):
    """
    Copied from robosuite
    """
    # clip quaternion
    if quat[3] > 1.0:
        quat[3] = 1.0
    elif quat[3] < -1.0:
        quat[3] = -1.0

    den = np.sqrt(1.0 - quat[3] * quat[3])
    if math.isclose(den, 0.0):
        # This is (close to) a zero degree rotation, immediately return
        return np.zeros(3)

    return (quat[:3] * 2.0 * math.acos(quat[3])) / den


class LIBEROEnv(BaseEnv):
    default_action = np.zeros(7)

    def __init__(self, task_suite_name, task_id, max_steps=500):
        benchmark_dict = benchmark.get_benchmark_dict()
        self.task_id = task_id
        self.task_suite = benchmark_dict[task_suite_name]()
        task = self.task_suite.get_task(task_id)

        task_bddl_file = os.path.join(
            get_libero_path("bddl_files"),
            task.problem_folder,
            task.bddl_file,
        )
        env_args = {
            "bddl_file_name": task_bddl_file,
            "camera_heights": 256,
            "camera_widths": 256,
        }
        self.env = OffScreenRenderEnv(**env_args)
        self.task_description = "Task Description: " + task.language

        # timer
        self.max_steps = max_steps
        self.current_step = 0
        self.current_obs = None

    def _process_obs(self, obs_dict):
        """
        Convert dict obs into flat obs for agent:
        concat [eef_pos(3), axisangle(3), gripper_qpos(2)] -> shape (8,)
        """
        eef_pos = obs_dict["robot0_eef_pos"]
        eef_quat = obs_dict["robot0_eef_quat"]
        eef_axis = quat2axisangle(eef_quat)
        gripper = obs_dict["robot0_gripper_qpos"]
        return np.concatenate([eef_pos, eef_axis, gripper])

    def step(self, keys):
        # TODO add action 3~5
        action = np.zeros(7)
        if 'a' in keys: action[1] += 1
        elif 'd' in keys: action[1] -= 1
        if 'w' in keys: action[0] -= 1
        elif 's' in keys: action[0] += 1
        if 'j' in keys: action[2] -= 1
        elif 'k' in keys: action[2] += 1
        if 'l' in keys: action[6] += 1
        elif 'o' in keys: action[6] -= 1

        obs_dict, rew, done, info = self.env.step(action)

        # timer
        self.current_step += 1
        truncated = self.current_step >= self.max_steps

        done = info.get("success", False) or done
        obs = self._process_obs(obs_dict)
        self.current_obs = obs_dict
        
        return (obs, rew, done, truncated, info), action

    def reset(self):
        self.current_step = 0
        obs_dict = self.env.reset()
        
        init_states = self.task_suite.get_task_init_states(self.task_id)
        ri = random.randint(0, 49)  # Max=50
        obs_dict = self.env.set_init_state(init_states[ri])
        
        self.current_obs = obs_dict
        
        return self._process_obs(obs_dict)

    def render(self):
        obs = self.current_obs
        return {
            "obs_agent": obs["agentview_image"][::-1, ::-1],
            "obs_griper": obs["robot0_eye_in_hand_image"],
        }
        
    @property
    def action_space(self):
        return gym.spaces.Box(
            low=-1.0, high=1.0, shape=(7,), dtype=np.float32
        )

    @property
    def observation_space(self):
        return gym.spaces.Box(
            low=-np.inf, high=np.inf, shape=(8,), dtype=np.float32
        )
        
    def close(self):
        return self.env.close()

import sys

# "libero_10", "libero_90", "libero_spatial", "libero_object", "libero_goal"
SUITES_TO_GENERATE = ["libero_object"]  # Add more suites as needed

# Store all generated class names for __all__
__all__ = []

current_module = sys.modules[__name__]

for suite_name in SUITES_TO_GENERATE:
    try:
        benchmark_dict = benchmark.get_benchmark_dict()
        task_suite = benchmark_dict[suite_name]()
        num_tasks = task_suite.n_tasks
    except Exception as e:
        print(f"Warning: Failed to load suite '{suite_name}': {e}")
        continue

    for task_id in range(num_tasks):
        task = task_suite.get_task(task_id)
        class_name = f"{suite_name}_task_{task_id}"

        # Avoid duplicates (theoretically unnecessary, but just in case)
        if hasattr(current_module, class_name):
            continue

        # Capture the current suite_name and task_id in a closure
        def make_init(ts_name, t_id):
            def __init__(self, max_steps=500):
                LIBEROEnv.__init__(self, ts_name, t_id, max_steps)
            return __init__

        new_class = type(
            class_name,
            (LIBEROEnv,),
            {
                "__init__": make_init(suite_name, task_id),
                "__module__": __name__,  # Important: let the class know which module it belongs to
                "__doc__": f"LIBERO task: {suite_name} - {task.name}\n{task.language}"
            }
        )

        # Bind the new class to the current module
        setattr(current_module, class_name, new_class)
        __all__.append(class_name)

# # debugging
# print(f"[libero_tasks] Generated {len(__all__)} task classes.")
# print(__all__)


# if __name__ == "__main__":
#     task_suite_name = "libero_object"
#     num_epoch = 50
#     seed = 0
    
#     benchmark_dict = benchmark.get_benchmark_dict()
#     task_suite = benchmark_dict[task_suite_name]()
#     num_tasks = task_suite.n_tasks  # 10
    
#     for task_id in range(num_tasks):
#         # retrieve a specific task
#         task = task_suite.get_task(task_id)
#         task_name = task.name
#         task_description = task.language
#         task_bddl_file = os.path.join(get_libero_path("bddl_files"), task.problem_folder, task.bddl_file)
#         print(f"[info] retrieving task {task_id} from suite {task_suite_name}, the " + \
#             f"language instruction is {task_description}, and the bddl file is {task_bddl_file}")
#         env_args = {
#             "bddl_file_name": task_bddl_file,
#             "camera_heights": 256,
#             "camera_widths": 256
#         }
#         env = OffScreenRenderEnv(**env_args)
#         env.seed(seed)
        
#         for epoch in range(num_epoch):
#             env.reset()
#             init_states = task_suite.get_task_init_states(task_id) # for benchmarking purpose, we fix the a set of initial states
#             env.set_init_state(init_states[epoch])

#             dummy_action = [0.] * 7
#             for step in range(10):
#                 obs, reward, done, info = env.step(dummy_action)
#             print(obs.keys())
#             # State
#             print(obs["robot0_eef_pos"].shape)  # (3,)
#             print(quat2axisangle(obs["robot0_eef_quat"]).shape)  # (3,)
#             print(obs["robot0_gripper_qpos"])  # (2)
#             # RGB
#             print(obs["agentview_image"].shape)  # (256, 256, 3)
#             print(obs["robot0_eye_in_hand_image"].shape)  # (256, 256, 3)
#             print(done)  # bool
#             print(reward)  # sparse reward
#             env.close()
            
#             break
#         break

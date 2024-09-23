import os
import argparse
from typing import Any, Dict, List, Tuple
import functools
import copy
from tqdm import tqdm
import cv2
import numpy as np
from numba import njit
import h5py
import metaworld.envs.mujoco.env_dict as _env_dict
from tests.metaworld.envs.mujoco.sawyer_xyz.test_scripted_policies import test_cases_latest_noisy

@njit
def clip_and_map_to_integers(arr):
    # 定义离散值集合
    discrete_values = np.array([-1, -0.9, -0.8, -0.7, -0.6, -0.5, -0.4, -0.3, -0.2, -0.1, 0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1])
    # 创建离散值到整数的查找表
    value_to_int_lookup = np.arange(len(discrete_values))
    flat_arr = arr.flatten()
    clipped_arr = np.zeros_like(flat_arr)
    mapped_arr = np.zeros_like(flat_arr, dtype=np.int64)

    for i in range(len(flat_arr)):
        closest_idx = np.argmin(np.abs(discrete_values - flat_arr[i]))
        clipped_arr[i] = discrete_values[closest_idx]
        mapped_arr[i] = value_to_int_lookup[closest_idx]

    return clipped_arr.reshape(arr.shape), mapped_arr.reshape(arr.shape)

def trajectory_generator(
    env: Any, policy: Any,
    res: Tuple[int, int] = (224, 224),
    camera: str = 'corner',
    max_path_length: int = 500
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Generate a trajectory in the environment."""
    env.reset()
    env.reset_model()
    obs = env.reset()
    # env.max_path_length = max_path_length

    for _ in range(env.max_path_length):
        action = policy.get_action(obs)
        obs, rew, done, info = env.step(action)
        rgb_image = env.sim.render(*res, mode='offscreen', camera_name=camera)[:,:,::-1]
        # mocap_pos = copy.deepcopy(env.data.mocap_pos)
        yield obs, rgb_image, action, info

def generate_trajectory(env: Any, env_name: str, idx: int, params: Dict[str, Any]) -> Tuple[str, int, Dict[str, List]]:
    """Generate a single trajectory."""
    env._partially_observable = False
    env._freeze_rand_vec = False
    env._set_task_called = True
    policy = functools.reduce(lambda a,b : a if a[0] == env_name else b, test_cases_latest_noisy)[1]
    tag = 0

    while tag < 20:
        data = {"obss": [], "obs_rgbs": [], "acts": []}
        for obs, obs_rgb, act, info in trajectory_generator(env, policy, params['resolution'], params['camera']):
            if params['flip']: obs_rgb = cv2.rotate(obs_rgb, cv2.ROTATE_180)
            data["obss"].append(obs)
            data["obs_rgbs"].append(obs_rgb)
            data["acts"].append(act)
            if info['success']:
                tag = 20
                break
        tag += 1
        if tag != 21: print(f"False {env_name} {idx}, last {20 - tag}.")
    
    return env_name, idx, data

def main(
    n_trajectories: int = 100,
    resolution: Tuple[int, int] = (224, 224),
    camera: str = 'corner',
    flip: bool = False,
    data_dir: str = './data',
    hdf5_filename: str = 'trajectories.hdf5'
):
    """Main function to generate trajectories and save to a single HDF5 file."""
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

    hdf5_file = os.path.join(data_dir, hdf5_filename)

    params = {'resolution': resolution, 'camera': camera, 'flip': flip,}

    # Get all environments from MT50_V2
    env_dict = _env_dict.MT50_V2.items()

    with h5py.File(hdf5_file, 'w') as f:
        pbar = tqdm(total=n_trajectories * len(env_dict), desc="Generating and writing trajectories")
        for env_name, env_class in env_dict:
            env = env_class()
            env_group = f.create_group(env_name)
            for idx in range(n_trajectories):
                _, _, data = generate_trajectory(env, env_name, idx, params)
                traj_group = env_group.create_group(str(idx))
                for key, value in data.items():
                    traj_group.create_dataset(key, data=np.array(value), compression="gzip")
                pbar.update(1)
        pbar.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate trajectories for MT50_V2 environments and save to a single HDF5 file.")
    parser.add_argument("--n_trajectories", type=int, default=100, help="Number of trajectories to generate per environment")
    parser.add_argument("--resolution", type=int, nargs=2, default=(224, 224), help="Resolution of the rendered image")
    parser.add_argument("--camera", type=str, default='corner', choices=['corner', 'topview', 'behindGripper', 'gripperPOV'], help="Camera angle for rendering")
    parser.add_argument("--flip", action="store_true", help="Flip output image 180 degrees")
    parser.add_argument("--data_dir", type=str, default='./data', help="Directory to save the data")
    parser.add_argument("--hdf5_filename", type=str, default='trajectories.hdf5', help="Name of the output HDF5 file")

    args = parser.parse_args()

    main(args.n_trajectories, tuple(args.resolution), args.camera, args.flip, args.data_dir, args.hdf5_filename)

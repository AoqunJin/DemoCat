import threading
from datetime import datetime
import h5py
import numpy as np
import os


class HDF5DataManager:
    def __init__(self, root_dir):        
        """
        Constructor for HDF5DataManager.

        Parameters
        ----------
        root_dir : str
            The directory where HDF5 files will be stored.
        """
        self.root_dir = root_dir
        os.makedirs(root_dir, exist_ok=True)
        self._lock = threading.Lock()

    def _get_file_path(self, env_name, task_name):
        """Return HDF5 file path for given env/task"""
        filename = f"{env_name}_{task_name}.hdf5"
        return os.path.join(self.root_dir, filename)

    def save_demonstration(self, env_name: str, task_name: str, demo_data):
        """
        Save a demonstration into the HDF5 file.

        Parameters
        ----------
        env_name : str
        task_name : str
        demo_data : dict
        """
        min_l = len(demo_data["action"])
        with self._lock:
            file_path = self._get_file_path(env_name, task_name)
            with h5py.File(file_path, 'a') as f:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                demo_group = f.require_group(timestamp)
                
                for key, value in demo_data.items():
                    if key == 'instruction':
                        dt = h5py.string_dtype(encoding='utf-8')
                        demo_group.create_dataset(key, data=value, dtype=dt)

                    elif isinstance(value, list) and len(value) > 0 and isinstance(value[0], dict):
                        for sub_key in value[0].keys():
                            stacked = np.stack([v[sub_key] for v in value[:min_l]])
                            demo_group.create_dataset(
                                f"{key}/{sub_key}", 
                                data=stacked, 
                                compression="gzip", 
                                chunks=True
                            )
                    else:
                        demo_group.create_dataset(
                            key, 
                            data=np.array(value[:min_l]), 
                            compression="gzip", 
                            chunks=True
                        )

    def load_demonstrations(self, env_name, task_name, timestamp):
        """
        Load a demonstration from the HDF5 file.
        """
        file_path = self._get_file_path(env_name, task_name)
        with self._lock:
            demonstrations = {}
            with h5py.File(file_path, 'r') as f:
                demo_group = f[timestamp]

                for key in demo_group.keys():
                    if key == 'instruction':
                        demonstrations[key] = demo_group[key][()]
                    elif isinstance(demo_group[key], h5py.Group):
                        sub_keys = list(demo_group[key].keys())
                        stacked_sub = [demo_group[key][sub_key][:] for sub_key in sub_keys]

                        demonstrations[key] = [
                            {sub_key: stacked_sub[i][j] if stacked_sub[i].ndim > 1 else stacked_sub[i][j] 
                            for i, sub_key in enumerate(sub_keys)}
                            for j in range(stacked_sub[0].shape[0])
                        ]
                    else:
                        demonstrations[key] = demo_group[key][:]
            
            return demonstrations

    def delete_demonstration(self, env_name, task_name, demo_id):
        file_path = self._get_file_path(env_name, task_name)
        with self._lock:
            with h5py.File(file_path, 'a') as f:
                del f[demo_id]

    def get_demonstration_list(self, env_name, task_name, page=1, page_size=10):
        """
        Get a list of demonstrations in the given env/task file.
        """
        file_path = self._get_file_path(env_name, task_name)
        with self._lock:
            demo_list = []
            try:
                with h5py.File(file_path, 'r') as f:
                    k = list(f.keys())
                    index = (page - 1) * page_size
                    for i, timestamp in enumerate(k):
                        if i < index:
                            continue
                        if i >= index + page_size:
                            break
                        demo_list.append(timestamp)
            except FileNotFoundError as e:
                print(e)
                return [], 1
            except KeyError as e:
                print(e)
                return [], 1
            return demo_list, (len(k) - 1) // page_size + 1

            
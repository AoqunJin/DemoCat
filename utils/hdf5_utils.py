import h5py
import numpy as np
import threading
from datetime import datetime

class HDF5DataManager:
    def __init__(self, file_path):
        self.file_path = file_path
        self._lock = threading.Lock()
        # TODO Add cache self._cache = {}

    def save_demonstration(self, env_name: str, task_name: str, demo_data):
        with self._lock:
            with h5py.File(self.file_path, 'a') as f:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                demo_group = f.require_group(f"{env_name}/{task_name}/{timestamp}")
                
                for key, value in demo_data.items():
                    if isinstance(value, dict):
                        # 创建子组
                        sub_group = demo_group.require_group(key)
                        for sub_key, sub_value in value.items():
                            sub_group.create_dataset(sub_key, data=np.array(sub_value), compression="gzip", chunks=True)
                    else:
                        demo_group.create_dataset(key, data=np.array(value), compression="gzip", chunks=True)

    def load_demonstrations(self, env_name, task_name):
        with self._lock:
            demonstrations = {}
            with h5py.File(self.file_path, 'r') as f:
               self._load_task_demonstrations(f[env_name][task_name], demonstrations, env_name, task_name)
            
            return demonstrations

    def _load_task_demonstrations(self, task_group, demonstrations, env_name, task_name):
        for timestamp in task_group.keys():
            demo_data = {}
            demo_group = task_group[timestamp]
            for key in demo_group.keys():
                demo_data[key] = demo_group[key][:]
            for key, value in demo_group.attrs.items():
                demo_data[key] = value
            demonstrations[f"{timestamp}"] = demo_data

    def delete_demonstration(self, env_name, task_name, demo_id):
        with self._lock:
            with h5py.File(self.file_path, 'a') as f:
                del f[f"{env_name}/{task_name}/{demo_id}"]

    def get_demonstration_list(self, env_name, task_name, page=1, page_size=10):
        with self._lock:
            demo_list = []
            try:
                with h5py.File(self.file_path, 'r') as f:
                    index = (page - 1) * page_size
                    k = list(f[env_name][task_name].keys())
                    for i, timestamp in enumerate(k):
                        if i < index:
                            continue
                        if i >= index + page_size:
                            break
                        demo_list.append(f"{env_name}/{task_name}/{timestamp}")
            except FileNotFoundError as e:
                print(e)
                return [], 1
            return demo_list, (len(k) + 1) // page_size + 1
            
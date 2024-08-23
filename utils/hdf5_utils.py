from functools import reduce
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
        # clip
        l = []
        for key, value in demo_data.items():
            if key != 'instruction': l.append(len(value))
        min_l = reduce(min, l)
        with self._lock:
            with h5py.File(self.file_path, 'a') as f:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                demo_group = f.require_group(f"{env_name}/{task_name}/{timestamp}")
                
                for key, value in demo_data.items():
                    if key == 'instruction':
                        dt = h5py.string_dtype(encoding='utf-8')
                        demo_group.create_dataset(key, data=value, dtype=dt,)
                    else:
                        demo_group.create_dataset(key, data=np.array(value[:min_l]), compression="gzip", chunks=True)

    def load_demonstrations(self, env_name, task_name, timestamp):
        with self._lock:
            demonstrations = {}
            with h5py.File(self.file_path, 'r') as f:
                demo_group = f[f"{env_name}/{task_name}/{timestamp}"]
                for key in demo_group.keys():
                    if key == 'instruction':
                        demonstrations[key] = demo_group[key][()]
                    else:
                        demonstrations[key] = demo_group[key][:]
            
            return demonstrations

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
            except KeyError as e:
                print(e)
                return [], 1
            return demo_list, (len(k) - 1) // page_size + 1
            
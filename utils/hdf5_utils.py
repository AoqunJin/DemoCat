from functools import reduce
import h5py
import numpy as np
import threading
from datetime import datetime

class HDF5DataManager:
    def __init__(self, file_path):        
        """
        Constructor for HDF5DataManager.

        Parameters
        ----------
        file_path : str
            The path to the HDF5 file to store the data in.

        """
        self.file_path = file_path
        self._lock = threading.Lock()
        # TODO Add cache self._cache = {}

    def save_demonstration(self, env_name: str, task_name: str, demo_data):
        """
        Save a demonstration into the HDF5 file.

        Parameters
        ----------
        env_name : str
            The name of the environment.
        task_name : str
            The name of the task.
        demo_data : dict
            A dictionary containing the demonstration data. The keys should be
            the names of the data, and the values should be the data itself. If
            the data is a string, it should be stored under the key
            'instruction'.

        Returns
        -------
        None
        """
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
        """
        Load a demonstration from the HDF5 file.

        Parameters
        ----------
        env_name : str
            The name of the environment.
        task_name : str
            The name of the task.
        timestamp : str
            The timestamp of the demonstration.

        Returns
        -------
        dict
            A dictionary containing the demonstration data. The keys should be
            the names of the data, and the values should be the data itself. If
            the data is a string, it should be stored under the key
            'instruction'.
        """
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
        """
        Get a list of demonstrations in the given environment and task.

        Parameters
        ----------
        env_name : str
            The name of the environment.
        task_name : str
            The name of the task.
        page : int, optional
            The page number to load, by default 1
        page_size : int, optional
            The number of demonstrations to load per page, by default 10

        Returns
        -------
        list
            A list of demonstration identifiers, each in the format
            'env_name/task_name/timestamp'.
        int
            The total number of pages of demonstrations available.
        """
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
            
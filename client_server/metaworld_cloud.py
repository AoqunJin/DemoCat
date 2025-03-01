import functools
import random
import copy
import logging
import threading
from absl import app, flags
import os
import shutil
import numpy as np
import wandb
from tqdm import tqdm

from metaworld_env import MetaworldEnv, _env_dict
from gym_wrappers import NormalizeProprio, HistoryWrapper, RHCWrapper, Manager


class EnvScheduler:
    _instance = None
    _lock = threading.Lock()  # 线程安全

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(EnvScheduler, cls).__new__(cls)
        return cls._instance
            
    def __init__(self, save_datadir=None, expert_rate=1, dataset_statistics=None):
        if not hasattr(self, "_initialized"):
            self._initialized = True
            # load finetuned model
            logging.info("Loading environment...")

            self.benchmark = _env_dict.MT10_V2
            self.save_datadir = save_datadir
            self.expert_rate = expert_rate
            self.dataset_statistics = dataset_statistics
            self.env_info = {}
            
            #####################################
            # Data
            #####################################
            
            if self.save_datadir:
                # if os.path.exists(self.save_datadir):
                #     shutil.rmtree(self.save_datadir, ignore_errors=True)
                os.makedirs(self.save_datadir, exist_ok=True)

            #####################################
            # Env
            #####################################

            for name in self.benchmark.keys():
                self.env_info[name] = {"last": 50}

    def get_env(self):
        rand_env = [(k, v) for k, v in self.env_info.items()]
        random.shuffle(rand_env)
        
        for k, v in rand_env:
            if v["last"] > 0:
                env = MetaworldEnv(k)

                # wrap env to normalize proprio
                if self.dataset_statistics is not None:
                    env = NormalizeProprio(env, self.dataset_statistics)

                # add wrappers for history and "receding horizon control", i.e. action chunking
                env = HistoryWrapper(env, horizon=2)  # optimize for models
                env = RHCWrapper(env, exec_horizon=1)                
                
                return Manager(env, k, self.save_datadir)
        
        return None
    
    def get_info(self):
        return self.env_info
    
    def set_info(self, info):
        self.env_info = info
        
import h5py
import numpy as np
from datetime import datetime

def modify_instructions(file_path):
    with h5py.File(file_path, 'r+') as f:
        for env_name in f.keys():
            for task_name in f[env_name].keys():
                for timestamp in f[f"{env_name}/{task_name}"].keys():
                    group_path = f"{env_name}/{task_name}/{timestamp}"
                    if 'instruction' in f[group_path]:
                        instruction = f[group_path]['instruction'][()]
                        if isinstance(instruction, bytes):
                            instruction = instruction.decode('utf-8')
                        
                        # Replace 'Cube' with 'Cylinder'
                            
                        modified_instruction = instruction.replace('Task description:', 'Task Description:')
                        
                        # Delete the original dataset
                        del f[group_path]['instruction']
                        
                        # Create a new dataset with the modified instruction
                        dt = h5py.string_dtype(encoding='utf-8')
                        f[group_path].create_dataset('instruction', data=modified_instruction, dtype=dt)
                        
                        print(f"Modified instruction in {group_path}")

if __name__ == "__main__":
    file_path = "/media/casia/52083A4F083A31F9/jinaoqun/workspace/DemoCat/data/demonstrations/demos.hdf5"  # Replace with your actual file path
    modify_instructions(file_path)
    print("Modification complete.")
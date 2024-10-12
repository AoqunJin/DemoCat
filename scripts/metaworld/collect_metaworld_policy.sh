export CUDA_VISIBLE_DEVICES="0"
export MUJOCO_GL="egl"

python policy_action.py --n_trajectories 20 --resolution 512 512 --camera corner --data_dir /home/ao/workspace/fs/diffusers --hdf5_filename trajectories_chunk_6.hdf5

# nohup bash collect_metaworld_policy.sh >out.log 2>&1 & disown
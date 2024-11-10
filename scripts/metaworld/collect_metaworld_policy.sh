export CUDA_VISIBLE_DEVICES=0
export MUJOCO_GL=osmesa
export PYOPENGL_PLATFORM=osmesa
# export DISPLAY=:0

python -u policy_action.py --n_trajectories 20 --resolution 512 512 --camera corner --data_dir /path/to/data --hdf5_filename trajectories_chunk_0.hdf5

# nohup bash collect_metaworld_policy.sh >out.log 2>&1 & disown

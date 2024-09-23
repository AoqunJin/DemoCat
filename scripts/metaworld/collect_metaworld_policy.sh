export CUDA_VISIBLE_DEVICES=0
python policy_action.py --n_trajectories 125 --resolution 224 224 --camera corner --data_dir /home/ao/workspace/fs/data/metaworld_data/policy/clip_freq80 --hdf5_filename trajectories_chunk_0.hdf5

# nohup bash collect_metaworld_policy.sh >out.log 2>&1 & disown
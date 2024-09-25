export CUDA_VISIBLE_DEVICES=0
xvfb-run -a python policy_action.py --n_trajectories 20 --resolution 512 512 --camera corner --data_dir /home/sora/workspace --hdf5_filename trajectories_chunk_0.hdf5

# nohup bash collect_metaworld_policy.sh >out.log 2>&1 & disown
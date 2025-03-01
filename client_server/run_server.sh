export CUDA_VISIBLE_DEVICES=1
# export JAX_PLATFORMS=cpu
# export MUJOCO_GL=egl
export MUJOCO_GL=osmesa
export DISPLAY=:0

python3 server.py

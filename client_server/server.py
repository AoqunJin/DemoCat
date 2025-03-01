import os

os.environ["CUDA_VISIBLE_DEVICES"] = "1"

import datetime
import time
import base64
import io
from flask import Flask, request, jsonify
from PIL import Image
import io
import numpy as np

from octo_inference import OctoInf
from metaworld_cloud import EnvScheduler
from stools import key_to_action

# TODO List:
# 加密与解密


def generate_white_noise_blocks(height=300, width=300, block_size=10):
    """
    生成花白色块的 NumPy 数组。
    
    参数：
    - height: 图片高度（像素）
    - width: 图片宽度（像素）
    - block_size: 每个块的大小（像素），越大块状感越明显
    
    返回：
    - img_array: 形状为 (height, width) 的 NumPy 数组（值范围 0-255）
    """
    # 计算块的行列数
    rows = height // block_size
    cols = width // block_size

    # 随机生成 0~255 之间的值，每个值代表一个 block
    block_values = np.random.randint(0, 256, size=(rows, cols), dtype=np.uint8)

    # 使用 np.kron 进行块复制，扩展到 full 图片
    img_array = np.kron(block_values, np.ones((block_size, block_size), dtype=np.uint8))

    return img_array


app = Flask(__name__)

# 服务器端存储的图片
IMAGE_ARRAY = generate_white_noise_blocks(height=300, width=300, block_size=10)
user_dict = {}
########################### Octo ##########################
jax_model = OctoInf("/home/jinaoqun/workspace/models/octo-base-metaworld_mt10")
dataset_statistics = jax_model.dataset_statistics
# dataset proprio to input proprio
for k in dataset_statistics["proprio"].keys():
    dataset_statistics["proprio"][k] = np.concatenate([
        dataset_statistics["proprio"][k][:6], dataset_statistics["proprio"][k][7:8],
    ])
########################### End Octo ########################
env_scheduler = EnvScheduler(
    dataset_statistics=dataset_statistics, 
    save_datadir="/home/jinaoqun/workspace/data/octo-base-h/metaworld_octo_base_c0"
)
collection_done = False

@app.route("/send_key", methods=["POST"])
def receive_key():
    global user_dict    
    global env_scheduler
    global collection_done
    global jax_model
    
    """接收按键并返回图片"""
    data = request.json
    key = data.get("key")
    uid = data.get("uid")
    env_info = env_scheduler.get_info()

    if collection_done:
        # 配置信息
        info = {"env_info": env_info, "iter_time": 500}
        # 发送图片
        image = Image.fromarray(IMAGE_ARRAY).resize((256, 256), Image.Resampling.LANCZOS)
        img_buffer = io.BytesIO()
        image.save(img_buffer, format="PNG")
        image_b64 = base64.b64encode(img_buffer.getvalue()).decode()

        return jsonify({"image": image_b64, "info": info})
    
    #####################################
    # user_dict 管理
    #####################################
    
    # Delete user after 10 minutes
    for k in list(user_dict.keys()):  # 先创建一个 keys 的副本
        if (datetime.datetime.now() - user_dict[k]["last_login_time"]).total_seconds() > 600:
            del user_dict[k]

    if uid not in user_dict:
        environment = env_scheduler.get_env()
        user_dict[uid] = {
            "environment": environment,
            "last_login_time": datetime.datetime.now(),
            "agent_run": False
        }  # Create a environment (New)
    else:  # 不接收创建环境的输入
        user_dict[uid]["last_login_time"] = datetime.datetime.now()
        if not user_dict[uid]["agent_run"]:
            action = jax_model.run(
                obs=user_dict[uid]["environment"].obs,
                language_instruction=user_dict[uid]["environment"].language_instruction
            )            
            for i in range(4):
                user_dict[uid]["environment"].step(action[i])
                # Remove finished environment
                if user_dict[uid]["environment"].done_or_trunc or \
                    env_info[user_dict[uid]["environment"].env_name]["last"] <= 0:
                    if user_dict[uid]["environment"].done:
                        env_info[user_dict[uid]["environment"].env_name]["last"] -= 1
                    del user_dict[uid]["environment"]
                    
                    environment = env_scheduler.get_env()
                    env_info = env_scheduler.get_info()
                    user_dict[uid]["environment"] = environment
                    break
            user_dict[uid]["agent_run"] = True
            
        elif key: 
            action = key_to_action(key)
            if action is not None:
                user_dict[uid]["agent_run"] = False
                user_dict[uid]["environment"].step(action, save=True)
                
                # Remove finished environment
                if user_dict[uid]["environment"].done_or_trunc or \
                    env_info[user_dict[uid]["environment"].env_name]["last"] <= 0:
                    if user_dict[uid]["environment"].done:
                        env_info[user_dict[uid]["environment"].env_name]["last"] -= 1
                    del user_dict[uid]["environment"]
                    
                    environment = env_scheduler.get_env()
                    env_info = env_scheduler.get_info()
                    user_dict[uid]["environment"] = environment

    # 所有任务完成
    if user_dict[uid]["environment"] is None:
        # collection_done = True  # TODO Update
       
        for k in list(user_dict.keys()):  # 先创建一个 keys 的副本
            del user_dict[k]
        env_scheduler.set_info({k: {"last": 50} for k in env_info.keys()})
        
        info = {"env_info": env_info, "iter_time": 500}
        image = Image.fromarray(IMAGE_ARRAY).resize((256, 256), Image.Resampling.LANCZOS)
    else:
        # 配置信息（还有多少环境、轨迹，当前的步数）
        info = {
            "env_info": env_info,
            "iter_time": user_dict[uid]["environment"].iter_time
        }
        # 发送图片
        image = Image.fromarray(
            user_dict[uid]["environment"].image
        ).resize((256, 256), Image.Resampling.LANCZOS)
        
    img_buffer = io.BytesIO()
    image.save(img_buffer, format="PNG")
    image_b64 = base64.b64encode(img_buffer.getvalue()).decode()

    return jsonify({"image": image_b64, "info": info})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9090, debug=False, threaded=False)
    
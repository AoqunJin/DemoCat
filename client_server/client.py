import datetime
import requests
import hashlib
import uuid
import base64
import io
import tkinter as tk
from PIL import Image, ImageTk
import numpy as np



def generate_sha256_id():
    unique_id = str(uuid.uuid4())  # 生成一个唯一的 UUID
    hash_id = hashlib.sha256(unique_id.encode()).hexdigest()  # 计算 SHA-256 哈希值
    return hash_id


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


def count_and_sum_positive_values(d):
    positive_keys = [k for k, v in d.items() if v["last"] > 0]
    count = len(positive_keys)
    total_sum = sum(d[k]["last"] for k in positive_keys)
    return count, total_sum


def get_image_and_info(response):
    data = response.json()
    image_b64 = data.get("image")
    info = data.get("info")

    image_data = base64.b64decode(image_b64)
    image = Image.open(io.BytesIO(image_data))
    image = image.resize((600, 600), Image.Resampling.LANCZOS)
    
    return image, info


# SERVER_URL = "http://10.6.44.93:5000/send_key"
SERVER_URL = "http://10.6.0.28:9090/send_key"
IMAGE_ARRAY = generate_white_noise_blocks(height=300, width=300, block_size=10)
# SERVER_URL = "http://127.0.0.1:5000/send_key"
UID = generate_sha256_id()


class KeyListenerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("数据采集器")
        self.root.geometry("900x900")

        # 显示主信息
        self.label = tk.Label(root, text="按任意按键开始", font=("Microsoft YaHei", 14))
        self.label.pack(pady=20)
        
        self.key_pressed_label = tk.Label(root, text="按下的按键: ", font=("Microsoft YaHei", 14))
        self.key_pressed_label.pack(pady=20)

        # 用于显示图片的 Label
        image = Image.fromarray(IMAGE_ARRAY)
        image = image.resize((600, 600), Image.Resampling.LANCZOS)
        
        self.tk_image = ImageTk.PhotoImage(image)
        self.image_label = tk.Label(root)
        self.image_label.pack(pady=20)
        self.image_label.config(image=self.tk_image)
        
        self.label_down = tk.Label(root, text="请使用英语键盘输入!\n提示：A D S W J K 上下左右前后 O L 夹爪", font=("Microsoft YaHei", 14))
        self.label_down.pack(pady=20)

        # 存储所有按下的按键
        self.pressed_keys = set()
        self.allowed_keys = {"a", "d", "s", "w", "j", "k", "l", "o"}

        # 绑定键盘事件
        root.bind("<KeyPress>", self.key_pressed)
        root.bind("<KeyRelease>", self.key_released)
        
        # 发送状态标志，防止重复调用 send_key
        self.sending = False
        self.last_time_empoty_sent = False
        
        # **定时触发 send_key，但保证不重复调用**
        self.schedule_send_key()
        
        self.image = None
        self.info = None

    def key_pressed(self, event):
        """当按键被按下时，添加到集合"""
        if event.keysym in self.allowed_keys:
            self.pressed_keys.add(event.keysym)
        self.update_label()

    def key_released(self, event):
        """当按键松开时，从集合中移除"""
        if event.keysym in self.pressed_keys:
            self.pressed_keys.remove(event.keysym)
        self.update_label()
        
    def update_label(self):
        """更新 GUI，显示当前按下的所有按键"""
        keys_text = "目前按下的按键: " + ", ".join(self.pressed_keys) if self.pressed_keys else "目前没有按键按下"
        self.key_pressed_label.config(text=keys_text)

    def schedule_send_key(self):
        """定时调用 send_key，但防止重复执行"""
        if not self.sending:  # 仅当上次任务已完成，才触发新任务
            self.sending = True
            self.send_key()

        # 每 500ms 重新检查是否可以调用 send_key
        self.root.after(5, self.schedule_send_key)

    def send_key(self):
        """发送按键到服务器并获取图片"""
        
        if "q" in self.pressed_keys:
            self.root.destroy()
            exit(0)
        try:
            #####################################
            # Get Image & Info
            #####################################
            if not self.last_time_empoty_sent:
                self.response = requests.post(SERVER_URL, json={"key": None, "uid": UID}, timeout=0.5)
                self.last_time_empoty_sent = True
                
            data = self.response.json()
            image_b64 = data.get("image")
            info = data.get("info")

            image_data = base64.b64decode(image_b64)
            image = Image.open(io.BytesIO(image_data))
            image = image.resize((600, 600), Image.Resampling.LANCZOS)

            self.tk_image = ImageTk.PhotoImage(image)
            self.image_label.config(image=self.tk_image)
            
            #####################################
            # Server Info
            #####################################
            # 环境、轨迹，当前的步数
            cas = count_and_sum_positive_values(info["env_info"])
            txt = f"剩余环境: {cas[0]} 剩余轨迹：{cas[1]}，当前行动步数：{info["iter_time"]} / 500"
            
            self.label.config(text=f"{txt}\n时间：{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            if len(self.pressed_keys) > 0:
                self.response = requests.post(SERVER_URL, json={"key": list(self.pressed_keys), "uid": UID}, timeout=0.5)
                self.last_time_empoty_sent = False
                
        except Exception as e:
            print(str(e))
            
            self.label.config(text=f"按键发送失败! 连接失败! 请联系开发者~ (提示: q 退出)\n时间：{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            image = Image.fromarray(IMAGE_ARRAY)
            image = image.resize((600, 600), Image.Resampling.LANCZOS)
            
            self.tk_image = ImageTk.PhotoImage(image)
            self.image_label.config(image=self.tk_image)

        finally:
            self.sending = False  # 允许下次调用

if __name__ == "__main__":
    root = tk.Tk()
    app = KeyListenerApp(root)
    root.mainloop()

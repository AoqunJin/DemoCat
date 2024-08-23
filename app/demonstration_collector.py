import time
import gc
import tkinter as tk
from tkinter import ttk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
from utils.input_handler import InputHandler
from utils.tools import resize_and_pad_to_square, trans

class DemonstrationCollector:
    def __init__(self, master, env_combobox, task_combobox, 
                 env_manager, data_manager, demo_listbox, task_info_text):
        self.master = master
        self.demonstration_data = []  # 存储演示数据的列表
        self.is_paused = False
        self.input_handler = InputHandler(master)

        self.env_combobox = env_combobox
        self.task_combobox = task_combobox
        self.env_manager = env_manager
        self.data_manager = data_manager
        self.demo_listbox = demo_listbox
        self.task_info_text = task_info_text
        self.demonstration_id = None
        self.is_demonstrating = False

        # 创建左侧面板
        left_panel = ttk.Frame(master)
        left_panel.grid(row=2, column=0, padx=10, pady=10)

        # 操作按钮区域
        action_frame = ttk.Frame(left_panel)
        action_frame.grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky=(tk.W, tk.E))

        # 画布区域：用于显示任务相关内容
        self.canvas = tk.Canvas(left_panel, width=500, height=500, background="white")
        self.canvas.grid(row=4, column=0, columnspan=2, padx=5, pady=5)

        # 操作按钮
        ttk.Button(action_frame, text="Start Environment", command=self.start_demonstration).pack(side=tk.LEFT, padx=5)
        self.save_button = ttk.Button(action_frame, text="Save Demonstration", command=self.save_demonstration, state=tk.DISABLED)
        self.save_button.pack(side=tk.LEFT, padx=5)
        self.pause_button = ttk.Button(action_frame, text="Pause", command=self.pause, state=tk.DISABLED)
        self.pause_button.pack(side=tk.LEFT, padx=5)
        self.master.bind_all("<p>", self.pause)
        self.master.bind_all("<q>", self.start_demonstration)
        self.master.bind_all("<e>", self.save_demonstration)

    def start_demonstration(self, event=None):
        if self.is_demonstrating:
            self.stop_demonstration()
            
        gc.collect()
        selected_env = self.env_combobox.get()
        selected_task = self.task_combobox.get()
        self.task = self.env_manager.create_task(selected_env, selected_task)
        self.input_handler.reset()
        self.is_demonstrating = True
        self.is_paused = False
        self.pause_button.configure(text="Pause")
        self.save_button['state'] = tk.NORMAL
        self.pause_button['state'] = tk.NORMAL
        self.demonstration_data = {"observation": [], "action": [], "reward": [], "done": [], "frames": [], "instruction": ""}
        observation = self.task.reset()
        img_array = self.task.render()
        self.demonstration_data["observation"].append(observation)
        self.demonstration_data["frames"].append(img_array)
        # self.demonstration_data["action"].append(self.task.default_action)  # Initial action
        # self.demonstration_data["reward"].append(0)
        # self.demonstration_data["done"].append(False)
        self.update_display()
        self.update_task_info()
        self.demonstration_id = self.master.after(50, self.step_environment)

    def step_environment(self):
        if self.is_demonstrating:
            done = False
            if not self.is_paused:
                action = self.input_handler.get_action()
                (observation, reward, terminated, truncated, info), action = self.task.step(action)
                done = terminated or truncated
                img_array = self.task.render()
                self.demonstration_data["observation"].append(observation)
                self.demonstration_data["action"].append(action)
                self.demonstration_data["reward"].append(reward)
                self.demonstration_data["done"].append(done)
                self.demonstration_data['instruction'] = self.task.task_description
                self.demonstration_data["frames"].append(img_array)
                self.update_display()

            if done:
                self.is_demonstrating = False
                self.pause_button['state'] = tk.DISABLED
            else:
                self.demonstration_id = self.master.after(50, self.step_environment)

    def stop_demonstration(self):
        if self.demonstration_id:
            self.master.after_cancel(self.demonstration_id)
        self.is_demonstrating = False
        self.pause_button['state'] = tk.DISABLED
        self.demonstration_id = None

    def update_display(self):
        img = Image.fromarray(trans(self.demonstration_data["frames"][-1]))
        img = resize_and_pad_to_square(img, 500)
        img = ImageTk.PhotoImage(img)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=img)
        self.canvas.image = img

    def save_demonstration(self, event=None):
        if str(self.save_button['state']) == tk.NORMAL:
            self.is_demonstrating = False
            self.save_button['state'] = tk.DISABLED
            self.pause_button['state'] = tk.DISABLED
            env_name = self.env_combobox.get()
            task_name = self.task_combobox.get()
            self.data_manager.save_demonstration(env_name, task_name, self.demonstration_data)
            # self.update_demo_list(env_name, task_name)
            messagebox.showinfo("Demonstration Saved", "Demonstration has been saved successfully.")

    def pause(self, event=None):
        if str(self.pause_button['state']) == tk.NORMAL:
            self.is_paused = not self.is_paused
            self.pause_button.configure(text="Continue" if self.is_paused else "Pause")

    def update_demo_list(self):
        self.demo_listbox.delete(0, tk.END)
        for demo in self.data_manager.get_demonstration_list():
            self.demo_listbox.insert(tk.END, demo)

    def update_task_info(self):
        info = self.task.task_description
        self.task_info_text.config(state=tk.NORMAL)
        self.task_info_text.delete('1.0', tk.END)
        self.task_info_text.insert(tk.END, f"{info}")
        self.task_info_text.config(state=tk.DISABLED)
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from utils.tools import resize_and_pad_to_square

class DemoPlayer:
    def __init__(self, master, demo_listbox):
        self.master = master
        self.is_playing = False
        self.new_demo = True
        self.current_frame = 0
        self.total_frames = 0
        self.demo_listbox = demo_listbox
        self.demonstration_data = None

        # 使用Grid布局
        self.playback = tk.Canvas(master, width=500, height=500, bg='white')
        self.playback.grid(row=0, column=0, columnspan=5, padx=10, pady=10, sticky='nsew')

        # 控制按钮
        button_frame = ttk.Frame(master)
        button_frame.grid(row=1, column=0, columnspan=5, pady=5, sticky='nsew')

        self.jump_to_start_button = ttk.Button(button_frame, text="|<<", command=self.jump_to_start, width=5)
        self.jump_to_start_button.grid(row=0, column=0, padx=5)

        self.rewind_button = ttk.Button(button_frame, text="<<", command=self.rewind, width=5)
        self.rewind_button.grid(row=0, column=1, padx=5)

        self.play_button = ttk.Button(button_frame, text="Play", command=self.play_pause, width=5)
        self.play_button.grid(row=0, column=2, padx=5)

        self.fast_forward_button = ttk.Button(button_frame, text=">>", command=self.fast_forward, width=5)
        self.fast_forward_button.grid(row=0, column=3, padx=5)

        self.jump_to_end_button = ttk.Button(button_frame, text=">>|", command=self.jump_to_end, width=5)
        self.jump_to_end_button.grid(row=0, column=4, padx=5)

        # 信息显示框
        self.info_text = tk.Text(master, height=4, width=70, bd='0')
        self.info_text.grid(row=2, column=0, columnspan=5, padx=10, pady=10, sticky='nsew')
        self.info_text.config(state=tk.DISABLED)

    def play_pause(self, demo_data=None):
        if demo_data:
            self.demonstration_data = demo_data
            self.is_playing = True
            self.play_demonstration()

        if self.is_playing:
            self.is_playing = False
            self.play_button.configure(text="Play")
        else:
            if self.current_frame == self.total_frames:
                self.current_frame = 0
                self.play_demonstration()

            self.is_playing = True
            self.play_button.configure(text="Pause")
            self.update_frame()

    def fast_forward(self):
        if self.current_frame < self.total_frames - 1:
            self.current_frame += 1
            self.update_frame()

    def rewind(self):
        if self.current_frame > 0:
            self.current_frame -= 1
            self.update_frame()

    def jump_to_start(self):
        self.current_frame = 0
        self.update_frame()

    def jump_to_end(self):
        self.current_frame = self.total_frames - 1
        self.update_frame()

    def play_demonstration(self):
        if self.demonstration_data:
            self.total_frames = len(self.demonstration_data['frames'])
            self.current_frame = 0
            self.update_frame()

    def update_frame(self):
        if self.current_frame < self.total_frames:
            img = Image.fromarray(self.demonstration_data['frames'][self.current_frame])
            img = resize_and_pad_to_square(img, 500)
            img = ImageTk.PhotoImage(img)
            self.playback.create_image(0, 0, anchor=tk.NW, image=img)
            self.playback.image = img
            
            self.info_text.config(state=tk.NORMAL)
            self.info_text.delete('1.0', tk.END)
            
            self.info_text.insert(tk.END, f"Instruction: {self.demonstration_data['instruction']}\n")
            self.info_text.insert(tk.END, f"Action: {self.demonstration_data['action'][self.current_frame]}\n")
            self.info_text.insert(tk.END, f"Done: {self.demonstration_data['done'][self.current_frame]}\n")
            
            # self.info_text.insert(tk.END, f"Reward: {self.demonstration_data['reward'][self.current_frame]}\n")
            # self.info_text.insert(tk.END, f"Observation: {self.demonstration_data['observation'][self.current_frame]}\n")
            self.info_text.config(state=tk.DISABLED)
            
            if self.is_playing:
                self.current_frame += 1
                self.master.after(100, self.update_frame)
        else:
            self.is_playing = False
            self.play_button.configure(text="Play")

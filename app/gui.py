import tkinter as tk
from tkinter import simpledialog
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
import numpy as np
from utils.input_handler import InputHandler
from app.demonstration_player import DemoPlayer
from app.demonstration_collector import DemonstrationCollector

class ImitationLearningGUI:
    def __init__(self, master, env_manager, data_manager):
        self.master = master
        self.env_manager = env_manager
        self.data_manager = data_manager
        self.input_handler = InputHandler(master)

        self.master.title("Imitation Learning Platform")
        self.master.geometry("1100x700")

        self.env = None
        self.task = None
        self.is_demonstrating = False
        self.is_paused = False
        self.demonstration_data = {"observation": [], "action": [], "reward": [], "done": [], "frames": []}
        
        self.current_page = 1
        self.total_pages = 10
        self.page_size = 10

        self.current_frame = 0
        self.total_frames = 0
        self.is_playing = False

        self.create_widgets()

    def create_widgets(self):
        # self.create_menu()
        self.create_tabs()

    def create_tabs(self):
        notebook = ttk.Notebook(self.master)
        notebook.pack(expand=1, fill='both')

        self.demo_tab = ttk.Frame(notebook)
        self.manage_tab = ttk.Frame(notebook)

        notebook.add(self.demo_tab, text='Demonstration Collection')
        notebook.add(self.manage_tab, text='Management')
        
        self.create_manage_tab_widgets()
        self.create_demo_tab_widgets()
        
    def create_demo_tab_widgets(self):
        # 左侧面板：包含环境和任务选择以及操作按钮
        top_panel = ttk.Frame(self.demo_tab, width=300, height=600)
        top_panel.grid(row=0, column=0, padx=10, pady=10, sticky=tk.NSEW)

        # 环境选择部分
        env_label = ttk.Label(top_panel, text="Environment:")
        env_label.grid(row=0, column=0, padx=5, pady=5, sticky=tk.E)
        self.env_combobox = ttk.Combobox(top_panel, values=self.env_manager.get_available_environments())
        self.env_combobox.grid(row=0, column=1, padx=5, pady=5, sticky=tk.E)
        self.env_combobox.config(state="readonly")

        # 任务选择部分
        task_label = ttk.Label(top_panel, text="Task:")
        task_label.grid(row=0, column=2, padx=5, pady=5, sticky=tk.E)
        self.task_combobox = ttk.Combobox(top_panel)
        self.task_combobox.grid(row=0, column=3, padx=5, pady=5, sticky=tk.E)
        self.task_combobox.config(state="readonly")

        # 将 bottom_panel 分为两部分
        bottom_panel = ttk.Frame(self.demo_tab, width=300)
        bottom_panel.grid(row=1, column=0, padx=10, pady=10, sticky=tk.NSEW)

        bottom_left_panel = ttk.Frame(bottom_panel)
        bottom_left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        bottom_right_panel = ttk.Frame(bottom_panel, width=40, height=60)
        bottom_right_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 10), pady=10)
        
        # 任务信息显示区域
        self.task_info_text = tk.Text(bottom_right_panel, height=20, width=50, font=("Calibri", 12), bd='0')
        self.task_info_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.task_info_text.config(state=tk.DISABLED)
        
        # 
        self.demonstration_collector = DemonstrationCollector(
            bottom_left_panel, self.env_combobox, self.task_combobox, 
            self.env_manager, self.data_manager, self.demo_listbox, self.task_info_text
        )

        # 设置默认环境值并绑定选择事件
        default_env = self.env_manager.get_available_environments()[0]
        self.env_combobox.set(default_env)
        self.env_combobox.bind("<<ComboboxSelected>>", self.update_task_combobox)
        self.update_task_combobox()

    def create_manage_tab_widgets(self):
        # 右侧面板
        right_panel = ttk.Frame(self.manage_tab, width=200, height=600)
        right_panel.grid(row=0, column=1, padx=10, pady=10, sticky=tk.NSEW)

        # 右上侧面板
        up_right_panel = ttk.Frame(right_panel)
        up_right_panel.grid(row=0, column=0, padx=10, pady=10, sticky=tk.NSEW)

        # 环境选择部分
        env_label = ttk.Label(up_right_panel, text="Environment:")
        env_label.grid(row=0, column=0, padx=5, pady=5, sticky=tk.E)
        self.env_combobox_manage = ttk.Combobox(up_right_panel, values=self.env_manager.get_available_environments())
        self.env_combobox_manage.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        self.env_combobox_manage.config(state="readonly")

        # 任务选择部分
        task_label = ttk.Label(up_right_panel, text="Task:")
        task_label.grid(row=0, column=2, padx=5, pady=5, sticky=tk.E)
        self.task_combobox_manage = ttk.Combobox(up_right_panel)
        self.task_combobox_manage.grid(row=0, column=3, padx=5, pady=5, sticky=tk.W)
        self.task_combobox_manage.config(state="readonly")

        # 右中侧面板
        mid_right_panel = ttk.Frame(right_panel)
        mid_right_panel.grid(row=1, column=0, padx=10, pady=10, sticky=tk.NSEW)

        history_label = ttk.Label(mid_right_panel, text="History:")
        history_label.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 演示显示区域
        self.demo_listbox = tk.Listbox(mid_right_panel, width=30, height=20, font=("Calibri", 12), bd='0')
        self.demo_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 创建框架
        frame = ttk.Frame(mid_right_panel, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建按钮
        ttk.Button(frame, text="|<<", command=self.first_page).grid(row=0, column=0)
        ttk.Button(frame, text="<", command=self.prev_page).grid(row=0, column=1)
        
        self.page_var = tk.StringVar()
        
        ttk.Label(frame, textvariable=self.page_var).grid(row=0, column=2, padx=10)
        
        ttk.Button(frame, text=">", command=self.next_page).grid(row=0, column=3)
        ttk.Button(frame, text=">>|", command=self.last_page).grid(row=0, column=4)

        # 右下侧面板
        bottom_right_panel = ttk.Frame(right_panel)
        bottom_right_panel.grid(row=2, column=0, padx=10, pady=10, sticky=tk.NSEW)

        ttk.Button(bottom_right_panel, text="Add To Player", command=self.view_demonstration).grid(row=0, column=0, padx=5, pady=5)
        ttk.Button(bottom_right_panel, text="Delete Demonstration", command=self.delete_demonstration).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(bottom_right_panel, text="Refresh", command=self.update_demo_list).grid(row=0, column=2, padx=5, pady=5)
        
        # 左侧面板
        left_panel = ttk.Frame(self.manage_tab, width=200, height=600)
        left_panel.grid(row=0, column=0, padx=10, pady=10, sticky=tk.NSEW)
        self.playback = DemoPlayer(left_panel, self.demo_listbox)

        # 设置默认环境值并绑定选择事件
        default_env = self.env_manager.get_available_environments()[0]
        self.env_combobox_manage.set(default_env)
        self.env_combobox_manage.bind("<<ComboboxSelected>>", self.update_task_combobox_manage)
        self.task_combobox_manage.bind("<<ComboboxSelected>>", self.update_demo_list)
        self.update_task_combobox_manage()
        self.update_page_display()

    def update_task_combobox(self, event=None):
        selected_env = self.env_combobox.get()
        tasks = self.env_manager.get_available_tasks(selected_env)
        self.task_combobox['values'] = tasks
        if tasks:
            self.task_combobox.set(tasks[0])
        else:
            self.task_combobox.set('')

    def update_task_combobox_manage(self, event=None):
        selected_env = self.env_combobox_manage.get()
        tasks = self.env_manager.get_available_tasks(selected_env)
        self.task_combobox_manage['values'] = tasks
        if tasks:
            self.task_combobox_manage.set(tasks[0])
        else:
            self.task_combobox_manage.set('')
        self.update_demo_list()

    def update_demo_list(self, event=None):
        env_name = self.env_combobox_manage.get()
        task_name = self.task_combobox_manage.get()
        self.demo_listbox.delete(0, tk.END)
        demo_list, total_pages = self.data_manager.get_demonstration_list(env_name, task_name, self.current_page, self.page_size)
        self.total_pages = total_pages
        
        for demo in demo_list:
            self.demo_listbox.insert(tk.END, demo)
        self.update_page_display()

    def update_page_display(self):
        self.page_var.set(f"{self.current_page} / {self.total_pages}")
        
    def first_page(self):
        self.current_page = 1
        self.update_demo_list()
        
    def prev_page(self):
        if self.current_page > 1:
            self.current_page -= 1
        self.update_demo_list()
        
    def next_page(self):
        if self.current_page < self.total_pages:
            self.current_page += 1
        self.update_demo_list()
        
    def last_page(self):
        self.current_page = self.total_pages
        self.update_demo_list()

    def view_demonstration(self):
        selected_demo = self.demo_listbox.get(tk.ACTIVE)
        if selected_demo:
            env_name, task_name, demo_id = selected_demo.split('/')
            demo_data = self.data_manager.load_demonstrations(env_name, task_name)[demo_id]
            self.playback.play_pause(demo_data)
        else:
            messagebox.showwarning("No Selection", "Please select a demonstration to view.")

    def delete_demonstration(self):
        selected_demo = self.demo_listbox.get(tk.ACTIVE)
        if selected_demo:
            if messagebox.askyesno("Delete Demonstration", f"Are you sure you want to delete the demonstration: {selected_demo}?"):
                env_name, task_name, demo_id = selected_demo.split('/')
                self.data_manager.delete_demonstration(env_name, task_name, demo_id)
                self.update_demo_list()
        else:
            messagebox.showwarning("No Selection", "Please select a demonstration to delete.")
            
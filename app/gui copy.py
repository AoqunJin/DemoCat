import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
import numpy as np
from utils.input_handler import InputHandler

class ImitationLearningGUI:
    def __init__(self, master, env_manager, data_manager):
        self.master = master
        self.env_manager = env_manager
        self.data_manager = data_manager
        self.input_handler = InputHandler(master)

        self.master.title("Imitation Learning Platform")
        self.master.geometry("1400x800")

        self.env = None
        self.task = None
        self.is_demonstrating = False
        self.is_paused = False
        self.demonstration_data = {"observation": [], "action": [], "reward": [], "done": [], "frames": []}
        
        self.current_frame = 0
        self.total_frames = 0
        self.is_playing = False

        self.create_widgets()

    def create_widgets(self):
        self.create_menu()
        self.create_main_frame()

    def create_menu(self):
        menubar = tk.Menu(self.master)
        self.master.config(menu=menubar)

        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Load Custom Task", command=self.load_custom_task)
        file_menu.add_command(label="Exit", command=self.master.quit)

    def create_main_frame(self):
        main_frame = ttk.Frame(self.master, padding="3 3 12 12")
        main_frame.grid(column=0, row=0, sticky=(tk.N, tk.W, tk.E, tk.S))
        self.master.columnconfigure(0, weight=1)
        self.master.rowconfigure(0, weight=1)

        # Left panel
        left_panel = ttk.Frame(main_frame)
        left_panel.grid(row=0, column=0, sticky=(tk.N, tk.W, tk.E, tk.S), padx=10)

        # Environment selection
        ttk.Label(left_panel, text="Select Environment:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.env_combobox = ttk.Combobox(left_panel, values=self.env_manager.get_available_environments())
        self.env_combobox.grid(row=0, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))
        self.env_combobox.set(self.env_manager.get_available_environments()[0])
        self.env_combobox.bind("<<ComboboxSelected>>", self.update_task_combobox)
        self.env_combobox.config(state="readonly")
        
        # Task selection
        ttk.Label(left_panel, text="Select Task:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.task_combobox = ttk.Combobox(left_panel)
        self.task_combobox.grid(row=1, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))
        self.task_combobox.config(state="readonly")
        
        # Task info
        self.task_info_text = tk.Text(left_panel, height=3, width=50)
        self.task_info_text.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky=(tk.W, tk.E))
        # self.task_info_text.config(state=tk.DISABLED)

        self.task_combobox.bind("<<ComboboxSelected>>", self.update_task_info)

        self.update_task_combobox()
        self.update_task_info()

        # Action buttons
        action_frame = ttk.Frame(left_panel)
        action_frame.grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky=(tk.W, tk.E))
        
        ttk.Button(action_frame, text="Start Demonstration", command=self.start_demonstration).pack(side=tk.LEFT, padx=5)
        self.save_button = ttk.Button(action_frame, text="Save Demonstration", command=self.save_demonstration, state=tk.DISABLED)
        self.save_button.pack(side=tk.LEFT, padx=5)
        self.pause_button = ttk.Button(action_frame, text="Pause", command=self.pause, state=tk.DISABLED)
        self.pause_button.pack(side=tk.LEFT, padx=5)

        # Canvas to display environment
        self.canvas = tk.Canvas(left_panel, width=500, height=500, background="white")
        self.canvas.grid(row=4, column=0, columnspan=2, padx=5, pady=5)

        # Demonstration info display
        self.info_text = tk.Text(left_panel, height=5, width=50)
        self.info_text.grid(row=5, column=0, columnspan=2, padx=5, pady=5, sticky=(tk.W, tk.E))

        # Playback control
        self.create_playback_control(left_panel)

        # Operation progress
        self.create_operation_progress(left_panel)

        # Right panel (demonstration list)
        right_panel = ttk.Frame(main_frame)
        right_panel.grid(row=0, column=1, sticky=(tk.N, tk.W, tk.E, tk.S), padx=10)

        ttk.Label(right_panel, text="Saved Demonstrations:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)

        self.demo_listbox = tk.Listbox(right_panel, width=40, height=20)
        self.demo_listbox.grid(row=1, column=0, padx=5, pady=5, sticky=(tk.N, tk.W, tk.E, tk.S))
        self.update_demo_list()

        # Operation buttons
        ttk.Button(right_panel, text="View Demonstration", command=self.view_demonstration).grid(row=2, column=0, padx=5, pady=5)
        ttk.Button(right_panel, text="Delete Demonstration", command=self.delete_demonstration).grid(row=3, column=0, padx=5, pady=5)

    def create_playback_control(self, parent):
        playback_frame = ttk.Frame(parent)
        playback_frame.grid(row=6, column=0, columnspan=2, padx=5, pady=5, sticky=(tk.W, tk.E))

        self.progress_var = tk.DoubleVar()
        self.progress_scale = ttk.Scale(playback_frame, from_=0, to=100, orient=tk.HORIZONTAL, variable=self.progress_var, command=self.seek)
        self.progress_scale.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.play_pause_button = ttk.Button(playback_frame, text="Play", command=self.toggle_play_pause)
        self.play_pause_button.pack(side=tk.LEFT, padx=5)

    def create_operation_progress(self, parent):
        progress_frame = ttk.Frame(parent)
        progress_frame.grid(row=7, column=0, columnspan=2, padx=5, pady=5, sticky=(tk.W, tk.E))

        ttk.Label(progress_frame, text="Operation Progress:").pack(side=tk.LEFT, padx=5)
        self.operation_progress = ttk.Progressbar(progress_frame, orient=tk.HORIZONTAL, length=200, mode='determinate')
        self.operation_progress.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

    def update_task_combobox(self, event=None):
        selected_env = self.env_combobox.get()
        tasks = self.env_manager.get_available_tasks(selected_env)
        self.task_combobox['values'] = tasks
        if tasks:
            self.task_combobox.set(tasks[0])
            self.update_task_info()
        else:
            self.task_combobox.set('')
            self.task_info_text.delete('1.0', tk.END)

    def update_task_info(self, event=None):
        selected_env = self.env_combobox.get()
        selected_task = self.task_combobox.get()
        if selected_env and selected_task:
            info = self.env_manager.get_task_info(selected_env, selected_task)
            self.task_info_text.delete('1.0', tk.END)
            self.task_info_text.insert(tk.END, f"Task Description: {info}\n")

    def load_custom_task(self):
        file_path = filedialog.askopenfilename(filetypes=[("Python files", "*.py")])
        if file_path:
            module_path = file_path.replace("/", ".").rstrip(".py")
            env_name = tk.simpledialog.askstring("Environment Name", "Enter the environment name:")
            class_name = tk.simpledialog.askstring("Class Name", "Enter the task class name:")
            if env_name and class_name:
                if self.env_manager.load_custom_task(env_name, module_path, class_name):
                    messagebox.showinfo("Success", f"Custom task '{class_name}' loaded successfully for environment '{env_name}'")
                    self.env_combobox['values'] = self.env_manager.get_available_environments()
                    self.update_task_combobox()
                else:
                    messagebox.showerror("Error", "Failed to load custom task")

    def start_demonstration(self):
        selected_env = self.env_combobox.get()
        selected_task = self.task_combobox.get()
        self.task = self.env_manager.create_task(selected_env, selected_task)
        self.input_handler.reset()
        self.is_demonstrating = True
        self.is_paused = False
        self.save_button['state'] = tk.NORMAL
        self.pause_button['state'] = tk.NORMAL
        self.demonstration_data = {"observation": [], "action": [], "reward": [], "done": [], "frames": []}
        observation = self.task.reset()
        self.demonstration_data["observation"].append(observation)
        self.demonstration_data["action"].append(0)  # Initial action
        self.demonstration_data["reward"].append(0)
        self.demonstration_data["done"].append(False)
        self.update_display()
        self.master.after(50, self.step_environment)

    def step_environment(self):
        if self.is_demonstrating:
            done = False
            if not self.is_paused:
                action = self.input_handler.get_action()
                (observation, reward, terminated, truncated, info), action = self.task.step(action)
                done = terminated or truncated

                self.demonstration_data["observation"].append(observation)
                self.demonstration_data["action"].append(action)
                self.demonstration_data["reward"].append(reward)
                self.demonstration_data["done"].append(done)
                self.update_display()

                # Update operation progress
                if hasattr(self.task, 'current_step') and hasattr(self.task, 'max_step'):
                    progress = (self.task.current_step / self.task.max_step) * 100
                    self.operation_progress['value'] = progress
                else:
                    self.operation_progress['value'] = 0 if done else 100

            if done:
                self.is_demonstrating = False
                self.pause_button['state'] = tk.DISABLED
            else:
                self.master.after(50, self.step_environment)

    def update_display(self):
        img_array = self.task.render()
        self.demonstration_data["frames"].append(img_array)
        img = Image.fromarray(img_array)
        img = ImageTk.PhotoImage(img)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=img)
        self.canvas.image = img

        # Update info display
        self.info_text.delete('1.0', tk.END)
        self.info_text.insert(tk.END, f"Observation: {self.demonstration_data['observation'][-1]}\n")
        self.info_text.insert(tk.END, f"Action: {self.demonstration_data['action'][-1]}\n")
        self.info_text.insert(tk.END, f"Reward: {self.demonstration_data['reward'][-1]}\n")
        self.info_text.insert(tk.END, f"Done: {self.demonstration_data['done'][-1]}")

    def save_demonstration(self):
        if self.demonstration_data:
            env_name = self.env_combobox.get()
            task_name = self.task_combobox.get()

            self.data_manager.save_demonstration(env_name, task_name, self.demonstration_data)
            self.update_demo_list()
            messagebox.showinfo("Demonstration Saved", "Demonstration has been saved successfully.")
            self.is_demonstrating = False
            self.save_button['state'] = tk.DISABLED
            self.pause_button['state'] = tk.DISABLED

    def pause(self):
        self.is_paused = not self.is_paused
        self.pause_button.configure(text="Continue" if self.is_paused else "Pause")

    def view_demonstration(self):
        selected_demo = self.demo_listbox.get(tk.ACTIVE)
        if selected_demo:
            env_name, task_name, demo_id = selected_demo.split('/')
            demo_data = self.data_manager.load_demonstrations(env_name, task_name)[demo_id]
            self.play_demonstration(demo_data)
        else:
            messagebox.showwarning("No Selection", "Please select a demonstration to view.")

    def play_demonstration(self, demo_data):
        self.is_demonstrating = False
        self.save_button['state'] = tk.DISABLED
        self.pause_button['state'] = tk.DISABLED
        self.demonstration_data = demo_data
        self.total_frames = len(demo_data['frames'])
        self.current_frame = 0
        self.is_playing = True
        self.play_pause_button.configure(text="Pause")
        self.update_frame()

    def update_frame(self):
        if self.is_playing and self.current_frame < self.total_frames:
            img = Image.fromarray(self.demonstration_data['frames'][self.current_frame])
            img = ImageTk.PhotoImage(img)
            self.canvas.create_image(0, 0, anchor=tk.NW, image=img)
            self.canvas.image = img

            self.info_text.delete('1.0', tk.END)
            self.info_text.insert(tk.END, f"Observation: {self.demonstration_data['observation'][self.current_frame]}\n")
            self.info_text.insert(tk.END, f"Action: {self.demonstration_data['action'][self.current_frame]}\n")
            self.info_text.insert(tk.END, f"Reward: {self.demonstration_data['reward'][self.current_frame]}\n")
            self.info_text.insert(tk.END, f"Done: {self.demonstration_data['done'][self.current_frame]}")

            self.progress_var.set((self.current_frame / (self.total_frames - 1)) * 100)
            self.current_frame += 1
            self.master.after(100, self.update_frame)
        elif self.current_frame >= self.total_frames:
            self.is_playing = False
            self.play_pause_button.configure(text="Play")

    def toggle_play_pause(self):
        if self.is_playing:
            self.is_playing = False
            self.play_pause_button.configure(text="Play")
        else:
            self.is_playing = True
            self.play_pause_button.configure(text="Pause")
            self.update_frame()

    def seek(self, value):
        if self.total_frames > 0:
            frame_index = int((float(value) / 100) * (self.total_frames - 1))
            self.current_frame = frame_index
            self.update_frame()

    def delete_demonstration(self):
        selected_demo = self.demo_listbox.get(tk.ACTIVE)
        if selected_demo:
            if messagebox.askyesno("Delete Demonstration", f"Are you sure you want to delete the demonstration: {selected_demo}?"):
                env_name, task_name, demo_id = selected_demo.split('/')
                self.data_manager.delete_demonstration(env_name, task_name, demo_id)
                self.update_demo_list()
        else:
            messagebox.showwarning("No Selection", "Please select a demonstration to delete.")

    def update_demo_list(self):
        self.demo_listbox.delete(0, tk.END)
        for demo in self.data_manager.get_demonstration_list():
            self.demo_listbox.insert(tk.END, demo)

    def update_operation_progress(self, current_step, max_step):
        if max_step > 0:
            progress = (current_step / max_step) * 100
            self.operation_progress['value'] = progress
        else:
            self.operation_progress['value'] = 0
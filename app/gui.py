import tkinter as tk
from tkinter import ttk, messagebox
from utils.input_handler import InputHandler
from app.demonstration_player import DemoPlayer
from app.demonstration_collector import DemonstrationCollector


class ImitationLearningGUI:
    def __init__(self, master, env_manager, data_manager):
        """
        Constructor for ImitationLearningGUI class.

        Parameters
        ----------
        master : tk.Tk
            The master window that this class will be attached to.
        env_manager : EnvironmentManager
            The manager that manages the environment.
        data_manager : DataManager
            The manager that manages the data.

        Returns
        -------
        None
        """
        self.master = master
        self.env_manager = env_manager
        self.data_manager = data_manager
        self.input_handler = InputHandler(master)

        self.master.title("Imitation Learning Platform")
        self.master.geometry("1280x720")

        self.env = None
        self.task = None
        self.is_demonstrating = False
        self.is_paused = False
        self.demonstration_data = {"observation": [], "action": [], "reward": [], "done": [], "frames": []}
        
        self.current_page = 1
        self.total_pages = 1
        self.page_size = 10

        self.current_frame = 0
        self.total_frames = 0
        self.is_playing = False

        self.create_widgets()

    def create_widgets(self):
        self.create_tabs()

    def create_tabs(self):
        """
        Create the tabs for demonstration collection and management.

        This function creates two tabs named "Demonstration Collection" and
        "Management". The first tab is for collecting and saving demonstrations,
        and the second tab is for managing the existing demonstrations.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        notebook = ttk.Notebook(self.master)
        notebook.pack(expand=1, fill='both')

        self.demo_tab = ttk.Frame(notebook)
        self.manage_tab = ttk.Frame(notebook)

        notebook.add(self.demo_tab, text=' Demonstration Collection ')
        notebook.add(self.manage_tab, text=' Management ')
        
        self.create_manage_tab_widgets()
        self.create_demo_tab_widgets()
        
    def create_demo_tab_widgets(self):
        """
        Create the widgets for the demonstration collection tab.

        This function creates a tab named "Demonstration Collection" and adds
        the necessary widgets to it. The widgets include a combobox for
        selecting the environment, a combobox for selecting the task, a
        demonstration collector, and a text box for displaying the task
        information.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        # Left panel: contains environment and task selection and operation buttons      
        top_panel = ttk.Frame(self.demo_tab, width=300, height=600)
        top_panel.grid(row=0, column=0, padx=10, pady=10, sticky=tk.NSEW)

        # Environment selection
        env_label = ttk.Label(top_panel, text=" Environment ")
        env_label.grid(row=0, column=0, padx=5, pady=5, sticky=tk.E)
        self.env_combobox = ttk.Combobox(top_panel, values=self.env_manager.get_available_environments())
        self.env_combobox.grid(row=0, column=1, padx=5, pady=5, sticky=tk.E)
        self.env_combobox.config(state="readonly")

        # Task selection
        task_label = ttk.Label(top_panel, text=" Task ")
        task_label.grid(row=0, column=2, padx=5, pady=5, sticky=tk.E)
        self.task_combobox = ttk.Combobox(top_panel)
        self.task_combobox.grid(row=0, column=3, padx=5, pady=5, sticky=tk.E)
        self.task_combobox.config(state="readonly")

        # Divide bottom_panel into two parts
        bottom_panel = ttk.Frame(self.demo_tab, width=300)
        bottom_panel.grid(row=1, column=0, padx=10, pady=10, sticky=tk.NSEW)

        # left_panel: use grid format
        bottom_left_panel = ttk.Frame(bottom_panel)
        bottom_left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # right_panel: use pack format
        bottom_right_panel = ttk.Frame(bottom_panel, width=40, height=60)
        bottom_right_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 10), pady=10)
        
        # Task information display area
        self.task_info_text = tk.Text(bottom_left_panel, height=60, width=50, bd='0',
                                      font=("Consolas", 16))
        self.task_info_text.grid(row=5, column=0, columnspan=2, padx=5, pady=5)
        self.task_info_text.config(state=tk.DISABLED)        
        # ↑↓
        # Demonstration Collector
        self.demonstration_collector = DemonstrationCollector(
            bottom_left_panel, self.env_combobox, self.task_combobox, 
            self.env_manager, self.data_manager, self.demo_listbox, self.task_info_text
        )
        
        # Control information display area
        self.control_info_text = tk.Text(bottom_right_panel, height=20, width=50, bd='0',
                                        font=("Consolas", 16))
        self.control_info_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Insert keybinding hints
        key_hints = "Key Bindings:\n\nP - Pause\nQ - Start Demonstration\nE - Save Demonstration"

        self.control_info_text.config(state="normal")
        self.control_info_text.insert("1.0", key_hints)

        # Set default environment value and bind selection event
        default_env = self.env_manager.get_available_environments()[0]
        self.env_combobox.set(default_env)
        self.env_combobox.bind("<<ComboboxSelected>>", self.update_task_combobox)
        self.update_task_combobox()

    def create_manage_tab_widgets(self):
        # Right panel
        """
        Create the widgets for the management tab.

        This function creates a tab named "Management" and adds
        the necessary widgets to it. The widgets include a combobox
        for selecting the environment, a combobox for selecting the
        task, a demonstration player, and a listbox for displaying
        the list of available demonstrations.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        
        right_panel = ttk.Frame(self.manage_tab, width=100, height=600)
        right_panel.grid(row=0, column=1, padx=10, pady=10, sticky=tk.NSEW)

        # Top right panel
        up_right_panel = ttk.Frame(right_panel)
        up_right_panel.grid(row=0, column=0, padx=10, pady=10)

        # Environment selection
        env_label = ttk.Label(up_right_panel, text=" Environment ")
        env_label.grid(row=0, column=0, padx=5, pady=5, sticky=tk.E)
        self.env_combobox_manage = ttk.Combobox(up_right_panel, values=self.env_manager.get_available_environments())
        self.env_combobox_manage.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        self.env_combobox_manage.config(state="readonly")

        # Task selection
        task_label = ttk.Label(up_right_panel, text=" Task ")
        task_label.grid(row=1, column=0, padx=5, pady=5, sticky=tk.E)
        self.task_combobox_manage = ttk.Combobox(up_right_panel)
        self.task_combobox_manage.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
        self.task_combobox_manage.config(state="readonly")

        # Middle right panel
        mid_right_panel = ttk.Frame(right_panel)
        mid_right_panel.grid(row=1, column=0, padx=10, pady=10)
        
        # History & Refresh
        his_ref_panel = ttk.Frame(mid_right_panel)
        his_ref_panel.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        
        # History label (left)
        history_label = ttk.Label(his_ref_panel, text=" History ")
        history_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        # Refresh button (right)
        refresh_button = ttk.Button(his_ref_panel, text=" Refresh ", command=self.update_demo_list)
        refresh_button.grid(row=0, column=1, padx=5, pady=5, sticky="e")

        # Demonstration display area (next row, span across both columns)
        self.demo_listbox = tk.Listbox(
            mid_right_panel, height=10, bd=0, font=("Consolas", 16)
        )
        self.demo_listbox.grid(row=2, column=0, columnspan=2, padx=10, pady=5, sticky="nsew")
        
        # Create frame
        frame = ttk.Frame(mid_right_panel,)
        frame.grid(row=3, column=0, padx=5, pady=5)
        
        # Create buttons
        ttk.Button(frame, text="|<<", command=self.first_page, width=5).grid(row=3, column=0)
        ttk.Button(frame, text="<", command=self.prev_page, width=5).grid(row=3, column=1)
        
        self.page_var = tk.StringVar()
        
        ttk.Label(frame, textvariable=self.page_var).grid(row=3, column=2, padx=10)
        
        ttk.Button(frame, text=">", command=self.next_page, width=5).grid(row=3, column=3)
        ttk.Button(frame, text=">>|", command=self.last_page, width=5).grid(row=3, column=4)

        # Bottom right panel
        bottom_right_panel = ttk.Frame(right_panel)
        bottom_right_panel.grid(row=2, column=0, padx=10, pady=10)

        ttk.Button(bottom_right_panel, text=" Add To Player ", command=self.view_demonstration).grid(row=0, column=0, padx=5, pady=5)
        ttk.Button(bottom_right_panel, text=" Delete ", command=self.delete_demonstration).grid(row=0, column=1, padx=5, pady=5)
        
        # Left panel
        left_panel = ttk.Frame(self.manage_tab, width=200, height=600)
        left_panel.grid(row=0, column=0, padx=10, pady=10, sticky=tk.NSEW)
        self.playback = DemoPlayer(left_panel, self.demo_listbox)

        # Set default environment value and bind selection event
        default_env = self.env_manager.get_available_environments()[0]
        self.env_combobox_manage.set(default_env)
        self.env_combobox_manage.bind("<<ComboboxSelected>>", self.update_task_combobox_manage)
        self.task_combobox_manage.bind("<<ComboboxSelected>>", self.update_page)
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
    
    def update_page(self, event=None):
        self.current_page = 1
        self.update_demo_list()

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
            self.demo_listbox.insert(tk.END, demo.split("/")[-1])
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
            env_name = self.env_combobox_manage.get()
            task_name = self.task_combobox_manage.get()
            demo_id = selected_demo
            demo_data = self.data_manager.load_demonstrations(env_name, task_name, demo_id)
            self.playback.play_pause(demo_data)
        else:
            messagebox.showwarning("No Selection", "Please select a demonstration to view.")

    def delete_demonstration(self):
        selected_demo = self.demo_listbox.get(tk.ACTIVE)
        if selected_demo:
            if messagebox.askyesno("Delete Demonstration", f"Are you sure you want to delete the demonstration: {selected_demo}?"):
                env_name = self.env_combobox_manage.get()
                task_name = self.task_combobox_manage.get()
                demo_id = selected_demo
                self.data_manager.delete_demonstration(env_name, task_name, demo_id)
                self.update_demo_list()
        else:
            messagebox.showwarning("No Selection", "Please select a demonstration to delete.")
            
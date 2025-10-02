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
        """
        Constructor for DemonstrationCollector class.

        Parameters
        ----------
        master : tk.Frame
            The master frame that this class will be attached to.
        env_combobox : ttk.Combobox
            The combobox that displays the list of available environment.
        task_combobox : ttk.Combobox
            The combobox that displays the list of available tasks.
        env_manager : EnvironmentManager
            The manager that manages the environment.
        data_manager : DataManager
            The manager that manages the data.
        demo_listbox : tk.Listbox
            The listbox that displays the list of available demonstrations.
        task_info_text : tk.Text
            The text box that displays the information of the current task.

        Returns
        -------
        None
        """
        self.master = master
        self.demonstration_data = []
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

        # Create left panel
        left_panel = ttk.Frame(master)
        left_panel.grid(row=2, column=0, padx=10, pady=10)

        # Create action frame
        action_frame = ttk.Frame(left_panel)
        action_frame.grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky=(tk.W, tk.E))

        # Create canvas
        self.canvas = tk.Canvas(left_panel, width=800, height=400, background="white")
        self.canvas.grid(row=4, column=0, columnspan=2, padx=5, pady=5)

        # Create buttons
        ttk.Button(action_frame, text=" Start Environment ", command=self.start_demonstration).pack(side=tk.LEFT, padx=5)
        self.save_button = ttk.Button(action_frame, text=" Save Demonstration ", command=self.save_demonstration, state=tk.DISABLED)
        self.save_button.pack(side=tk.LEFT, padx=5)
        self.pause_button = ttk.Button(action_frame, text=" Pause ", command=self.pause, state=tk.DISABLED)
        self.pause_button.pack(side=tk.LEFT, padx=5)
        self.master.bind_all("<p>", self.pause)
        self.master.bind_all("<q>", self.start_demonstration)
        self.master.bind_all("<e>", self.save_demonstration)

    def start_demonstration(self, event=None):
        """
        Start a demonstration environment.

        If a demonstration is already running, stop it first.

        Parameters
        ----------
        event : Event, optional
            The event that triggered this function call, by default None

        Returns
        -------
        None
        """
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
        frame = self.task.render()
        self.demonstration_data["observation"].append(observation)
        self.demonstration_data["frames"].append(frame)

        self.update_display()
        self.update_task_info()
        self.demonstration_id = self.master.after(50, self.step_environment)

    def step_environment(self):
        """
        Step the environment.

        If a demonstration is running, step the environment using the current action
        from the input handler. If the environment is not paused, render the
        environment and update the display.

        If the environment is done, stop the demonstration and disable the pause button.

        Otherwise, schedule the next step using `after`.

        Returns
        -------
        None
        """
        if self.is_demonstrating:
            done = False
            if not self.is_paused:
                action = self.input_handler.get_action()
                (observation, reward, terminated, truncated, info), action = self.task.step(action)
                done = terminated or truncated
                frame = self.task.render()
                self.demonstration_data["observation"].append(observation)
                self.demonstration_data["action"].append(action)
                self.demonstration_data["reward"].append(reward)
                self.demonstration_data["done"].append(done)
                self.demonstration_data['instruction'] = self.task.task_description
                self.demonstration_data["frames"].append(frame)
                self.update_display()

            if done:
                self.is_demonstrating = False
                self.pause_button['state'] = tk.DISABLED
            else:
                self.demonstration_id = self.master.after(50, self.step_environment)

    def stop_demonstration(self):
        """
        Stop the current demonstration.

        If a demonstration is currently running, stop it by cancelling the
        scheduled `after` call and resetting the demonstration state.

        Returns
        -------
        None
        """
        if self.demonstration_id:
            self.master.after_cancel(self.demonstration_id)
        self.is_demonstrating = False
        self.pause_button['state'] = tk.DISABLED
        self.demonstration_id = None

    def update_display(self):
        """
        Update the display of the current demonstration.

        This function updates the display of the current demonstration by
        rendering the current frame of the demonstration and displaying it
        on the canvas. If the frame is a dict, it concatenates all values
        horizontally after resizing and padding each to square.

        Returns
        -------
        None
        """
        frame = self.demonstration_data["frames"][-1]

        if isinstance(frame, dict):
            images = [resize_and_pad_to_square(Image.fromarray(trans(v)), 400) for v in frame.values()]
            widths, heights = zip(*(img.size for img in images))
            total_width = sum(widths)
            max_height = max(heights)
            new_img = Image.new('RGB', (total_width, max_height))
            x_offset = 0
            for img in images:
                new_img.paste(img, (x_offset, 0))
                x_offset += img.width
            img = new_img
        else:
            img = resize_and_pad_to_square(Image.fromarray(trans(frame)), 400)

        img = ImageTk.PhotoImage(img)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=img)
        self.canvas.image = img

    def save_demonstration(self, event=None):
        """
        Save the current demonstration.

        If the save button is currently enabled, this function will disable
        the save and pause buttons, and then save the current demonstration
        to the data manager.

        Parameters
        ----------
        event : Event, optional
            The event that triggered this function call, by default None

        Returns
        -------
        None
        """
        if str(self.save_button['state']) == tk.NORMAL:
            self.is_demonstrating = False
            self.save_button['state'] = tk.DISABLED
            self.pause_button['state'] = tk.DISABLED
            env_name = self.env_combobox.get()
            task_name = self.task_combobox.get()
            self.data_manager.save_demonstration(env_name, task_name, self.demonstration_data)
            messagebox.showinfo("Demonstration Saved", "Demonstration has been saved successfully.")

    def pause(self, event=None):
        """
        Pause or unpause the demonstration environment.

        If the pause button is currently enabled, this function will toggle
        the pause state of the demonstration environment. If the demonstration
        is paused, the pause button will display the text "Continue", and if
        the demonstration is not paused, the pause button will display the
        text "Pause".

        Parameters
        ----------
        event : Event, optional
            The event that triggered this function call, by default None

        Returns
        -------
        None
        """
        if str(self.pause_button['state']) == tk.NORMAL:
            self.is_paused = not self.is_paused
            self.pause_button.configure(text="Continue" if self.is_paused else "Pause")

    def update_demo_list(self):
        """
        Update the listbox with the latest list of demonstrations.

        This function will delete all the current items in the listbox and
        then insert the latest list of demonstrations retrieved from the
        data manager.

        Returns
        -------
        None
        """
        self.demo_listbox.delete(0, tk.END)
        for demo in self.data_manager.get_demonstration_list():
            self.demo_listbox.insert(tk.END, demo)

    def update_task_info(self):
        info = self.task.task_description
        """
        Update the task info text box with the latest task information.

        This function will enable the text box, delete its current contents,
        and then insert the latest task information retrieved from the task
        object. Finally, this function will re-disable the text box.

        Returns
        -------
        None
        """
        self.task_info_text.config(state=tk.NORMAL)
        self.task_info_text.delete('1.0', tk.END)
        self.task_info_text.insert(tk.END, f"{info}")
        self.task_info_text.config(state=tk.DISABLED)
        
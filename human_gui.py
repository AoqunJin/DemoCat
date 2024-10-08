# file: main.py

import tkinter as tk
from tkinter import ttk

from app.gui import ImitationLearningGUI
from app.environment import EnvironmentManager
from utils.hdf5_utils import HDF5DataManager

def main():
    """
    The main entry point of the application.

    This function creates a tkinter window and set up the style of the window.
    Then it creates an instance of EnvironmentManager and HDF5DataManager.
    Finally, it creates an instance of ImitationLearningGUI and starts the main loop of the application.

    """
    root = tk.Tk()
    root.config(bg="white")
    style = ttk.Style(root)
    # Available on all platform: alt, clam, classic, default
    # Windows: vista, winnative, xpnative
    # Mac: aqua
    # on Linux unfortunately there isn't any native theme, they look like plain tk widgets
    style.theme_use('clam')
    font_settings = ("Helvetica", 12)
    style.configure("TButton", foreground="black", font=font_settings, bg="white")
    style.configure("TLabel", foreground="black", font=font_settings, bg="white")
    style.configure("TCombobox", foreground="black", font=font_settings, bg="white")
    style.configure("Custom", background="white", font=font_settings)
    style.configure("TNotebook", background="white", font=font_settings)
    style.configure("TFrame", background="white", font=font_settings)

    env_manager = EnvironmentManager()
    data_manager = HDF5DataManager("data/demonstrations/demos.hdf5")
    app = ImitationLearningGUI(root, env_manager, data_manager)
    root.mainloop()

if __name__ == "__main__":
    main()

# file: main.py

import tkinter as tk
from tkinter import ttk
from ttkthemes import ThemedTk

from app.gui import ImitationLearningGUI
from app.environment import EnvironmentManager
from utils.hdf5_utils import HDF5DataManager

def main():
    root = tk.Tk()
    root.config(bg="white")
    style = ttk.Style()
    font_settings = ("Calibri", 12)
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
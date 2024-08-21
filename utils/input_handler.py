# file: utils/input_handler.py

import tkinter as tk
import gym

class InputHandler:
    def __init__(self, master):
        self.master = master
        self.key_pressed = set()
        self.mouse_position = (0, 0)
        self.mouse_clicked = False

        self.setup_bindings()

    def setup_bindings(self):
        self.master.bind("<KeyPress>", self.on_key_press)
        self.master.bind("<KeyRelease>", self.on_key_release)
        self.master.bind("<Motion>", self.on_mouse_move)
        self.master.bind("<Button-1>", self.on_mouse_click)
        self.master.bind("<ButtonRelease-1>", self.on_mouse_release)

    def on_key_press(self, event):
        self.key_pressed.add(event.keysym)

    def on_key_release(self, event):
        self.key_pressed.discard(event.keysym)

    def on_mouse_move(self, event):
        self.mouse_position = (event.x, event.y)

    def on_mouse_click(self, event):
        self.mouse_clicked = True

    def on_mouse_release(self, event):
        self.mouse_clicked = False

    def get_action(self):
        return self.key_pressed

    def reset(self):
        self.key_pressed.clear()
        self.mouse_position = (0, 0)
        self.mouse_clicked = False
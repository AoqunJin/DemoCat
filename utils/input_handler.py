import os


class InputHandler:
    def __init__(self, master):
        self.master = master
        self.key_pressed = set()
        self.mouse_position = (0, 0)
        self.mouse_clicked = False
        os.system("xset r on")
        self.setup_bindings()

    def setup_bindings(self):
        """
        Set up the event bindings for the master widget.

        This method is called in the constructor and sets up the
        event bindings for the master widget. The event bindings
        are as follows:

        - `<KeyPress>`: calls `on_key_press`
        - `<KeyRelease>`: calls `on_key_release`
        - `<Motion>`: calls `on_mouse_move`
        - `<Button-1>`: calls `on_mouse_click`
        - `<ButtonRelease-1>`: calls `on_mouse_release`
        """
        self.master.bind_all("<KeyPress>", self.on_key_press)
        self.master.bind_all("<KeyRelease>", self.on_key_release)
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
        
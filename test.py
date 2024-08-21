import tkinter as tk

class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Key Press Example")
        
        # Bind the "q" key press event to the on_q_key_press method
        self.bind("<q>", self.on_q_key_press)

    def on_q_key_press(self, event):
        # This method will be called when the "q" key is pressed
        print("The 'q' key was pressed!")

if __name__ == "__main__":
    app = Application()
    app.mainloop()

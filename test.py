import tkinter as tk
from tkinter import ttk

root = tk.Tk()

# 创建一个Style对象
style = ttk.Style()

# 设置全局背景颜色为白色
root.configure(bg="white")

# 设置不同小部件的样式
style.configure("TFrame", background="white")
style.configure("TLabel", background="white", foreground="#663399")  # 颜色为紫色
style.configure("TButton", background="#663399", foreground="white")  # 按钮背景紫色，文字白色
style.map("TButton",
          background=[("active", "#7D3C98"), ("pressed", "#4A235A")],  # 按下和悬停时的颜色
          foreground=[("active", "white"), ("pressed", "white")])

style.configure("TNotebook", background="white", borderwidth=0)
style.configure("TNotebook.Tab", background="#D8BFD8", foreground="#4B0082")  # 选项卡背景为淡紫色
style.map("TNotebook.Tab",
          background=[("selected", "#E6E6FA")],  # 选中时的背景颜色
          foreground=[("selected", "#4B0082")])  # 选中时的文字颜色

# 创建Notebook并添加标签页
notebook = ttk.Notebook(root)
notebook.pack(fill="both", expand=True, padx=10, pady=10)

frame1 = ttk.Frame(notebook)
frame2 = ttk.Frame(notebook)

notebook.add(frame1, text="Tab 1")
notebook.add(frame2, text="Tab 2")

# 在Frame1中添加标签和按钮
label1 = ttk.Label(frame1, text="这是一个标签")
label1.pack(pady=20)

button1 = ttk.Button(frame1, text="这是一个按钮")
button1.pack(pady=10)

# 在Frame2中添加其他组件
label2 = ttk.Label(frame2, text="另一个标签")
label2.pack(pady=20)

button2 = ttk.Button(frame2, text="另一个按钮")
button2.pack(pady=10)

root.mainloop()

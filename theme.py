# theme.py
import tkinter.ttk as ttk  # 꼭 tkinter꺼 써야 함!

def apply_theme(root):
    style = ttk.Style()
    style.theme_use("clam")

    style.configure("Cool.TButton",
        font=("맑은 고딕", 10, "bold"),
        foreground="#ffffff",
        background="#007acc",
        padding=6)

    style.map("Cool.TButton",
        background=[("active", "#005b99")])

    root.configure(bg="#f0f4f8")

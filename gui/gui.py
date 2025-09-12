import tkinter as tk
from tkinter import ttk
from typing import Any, Callable


class BaseGUI:
    def __init__(self, title: str = "Application", geometry: str = "800x600"):
        self.root: tk.Tk = tk.Tk()
        self.root.title(title)
        self.root.geometry(geometry)

        self.style: ttk.Style = ttk.Style()
        self.configure_styles()

        self.widgets: dict[str, tk.Widget] = {}
        self.callbacks: dict[str, Callable[..., Any]] = {}

    def configure_styles(self) -> None:
        self.style.theme_use("clam")

    def run(self) -> None:
        self.root.mainloop()

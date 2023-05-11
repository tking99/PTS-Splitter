import tkinter as tk


class MainNavbar(tk.Menu):
    def __init__(self, controller, *args, **kwargs):
        tk.Menu.__init__(self, controller, *args, **kwargs)
        self.controller = controller
        # file Menu
        self.file_menu = tk.Menu(self, tearoff=0)
        self.add_cascade(label="Tools", menu=self.file_menu)
        self.file_menu.add_command(label='Grid Splitter', command=self.controller.grid_splitter)
        self.file_menu.add_command(label='Pod Uploader', command=self.controller.pod_uploader)
        self.file_menu.add_command(label="Exit", command=self.controller.exit)

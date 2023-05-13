import os
import time
from datetime import datetime 
from sys import exit 
from pathlib import Path

import tkinter as tk 
from tkinter import ttk
from tkinter import messagebox
from tkinter.filedialog import askopenfilenames

from importers import GridImporter
from display import GridSplitterDisplay, PodExcellWritterDisplay
from models import ImportedFileOrgainser
from navigation import MainNavbar


class PTSSplitter(tk.Tk):
    DEFAULT_GRID = 'default_files/Grids_All.csv'
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.geometry("500x500")
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.title('Grid Splitter')
        # auto read grids into system - no checking has been applied
        self.wgrids = GridImporter.read(self.DEFAULT_GRID)
        self.nav_menu = MainNavbar(self, tearoff=0)
        self.config(menu=self.nav_menu)
        self.pts_files = []
        self.import_orgainser = ImportedFileOrgainser()
        self.import_pod_orgainser = ImportedFileOrgainser()
        self.main_frame = None
        self.grid_splitter()
        self.current_wgrid = None 
        
    def refresh_main(self):
        if self.main_frame is not None:
            self.main_frame.grid_forget()
            self.main_frame.destroy()
    
    def grid_splitter(self):
        self.refresh_main()
        self.main_frame = GridSplitterDisplay(self)
        self.main_frame.grid(column=0, row=0, padx=5, pady=5, sticky='NESW')

    def pod_uploader(self):
        self.refresh_main()
        self.main_frame = PodExcellWritterDisplay(self)
        self.main_frame.grid(column=0, row=0, padx=5, pady=5, sticky='NESW')
       
    def get_wgrid(self, x, y):
        # check first if current grid is correct and probably will be
        if self.current_wgrid is not None and self.current_wgrid.check_point(x, y):
            return self.current_wgrid
        for grid in self.wgrids:
            if grid.check_point(x, y):
                self.current_wgrid = grid 
                return grid
        ########### raise exception if not #########
            
    def exit(self):
        """Asks if user wants to save before 
        exiting out of the program"""
        answer = messagebox.askyesnocancel(
                title='Quit', message='Are you sure you want to quit?')
        if answer:
            exit()  
      
     
end_trial = datetime.strptime('01-08-2023', '%d-%m-%Y')

if __name__ == "__main__":
    if datetime.today() < end_trial:
        main = PTSSplitter()
        main.protocol('WM_DELETE_WINDOW', main.exit)
        main.mainloop()
    else:
        tk.messagebox.showerror(title='Version Error',
            message='Please contact Tom King for latest version.')














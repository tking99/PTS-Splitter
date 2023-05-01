from datetime import datetime
import datetime as dt
import tkinter as tk 
from tkinter import ttk
from tkinter.filedialog import askopenfilenames, askdirectory
from threading import Thread

from models import ImportedFile
from processer import PTSFileProcessor


class MainDisplay(ttk.Frame):
    ALLOWED_FILE_TYPES = (('PTS', '.pts'),)
    GRID_OPTIONS = ('1000', '500', '100', '50', '20') 

    def __init__(self, controller, *args, **kwargs):
        super().__init__(controller, *args, **kwargs)
        self.controller = controller
        self.import_frame = ttk.Frame(self)
        self.import_frame.grid(column=0, row=0, sticky='NW')
        self.pts_processor = PTSFileProcessor(self.controller.import_orgainser, self.controller)

        ttk.Label(self.import_frame, text='Step 1: Select PTS Files to Split:').grid(column=0, row=0, padx=5, pady=5)
        ttk.Button(self.import_frame, text='Select', command=self.import_files).grid(column=1, row=0, padx=5, pady=5)

        self.import_tree_display = ttk.Frame(self)
        self.import_tree_display.grid(column=0, row=1, sticky='NW', padx=5, pady=5)

        ttk.Separator(self, orient=tk.HORIZONTAL).grid(column=0, row=2, columnspan=10, sticky='EW')
        
        self.options_frame = ttk.Frame(self)
        self.options_frame.grid(column=0, row=3, sticky='NW')
        ttk.Label(self.options_frame, text='Step 2: Select Split Method').grid(column=0, row=0, padx=5, pady=5, sticky='NW') 
        self.split_by_grid = tk.BooleanVar(value=True)
        self.split_by_mb = tk.BooleanVar(value=False)
        
        self.option_choices_frame = ttk.Frame(self.options_frame)
        self.option_choices_frame.grid(column=0, row=1, sticky='NW')
        ttk.Checkbutton(self.option_choices_frame, variable=self.split_by_grid, onvalue=True,
            offvalue=False).grid(column=0, row=0, pady=5, padx=5, sticky='NW')
        ttk.Label(self.option_choices_frame, text='Split by SCS Grid').grid(column=1, row=0, sticky='NW')
        ttk.Label(self.option_choices_frame, text='Grid Size:').grid(column=2, row=0, sticky='NW')
        self.grid_size = tk.StringVar()
        option_menu = ttk.OptionMenu(
            self.option_choices_frame,
            self.grid_size,
            self.GRID_OPTIONS[0],
            *self.GRID_OPTIONS)
        option_menu.grid(column=3, row=0, sticky='NW')

        ttk.Checkbutton(self.option_choices_frame, variable=self.split_by_mb, onvalue=True,
            offvalue=False, state= "disabled").grid(column=0, row=1, pady=5, padx=5, sticky='NW')
        ttk.Label(self.option_choices_frame, text='Split by File Size (MB)').grid(column=1, row=1)

        
        
        description_frame = ttk.Frame(self)
        description_frame.grid(column=0, row=4, sticky='NW')

        self.description = tk.StringVar()
        self.survey_type = tk.StringVar()
        ttk.Label(description_frame, text='Add Survey Description: ').grid(column=0, row=0, sticky='NW', pady=5, padx=5)
        ttk.Entry(description_frame, width=30, textvariable=self.description).grid(
            column=1, row=0, sticky='NW', pady=5, padx=5)
        ttk.Label(description_frame, text='Add Survey Type: ').grid(column=0, row=1, sticky='NW', pady=5, padx=5)
        ttk.Entry(description_frame, width=30, textvariable=self.survey_type).grid(
            column=1, row=1, sticky='NW', pady=5, padx=5)

        



        self.export_frame = ttk.Frame(self)
        self.export_frame.grid(column=0, row=6, sticky='NW')
        ttk.Button(self.export_frame, text='SPLIT', command=self.split).grid(column=0, row=0, sticky='NW',
            pady=20, padx=5)

    def split(self):
        """splits the files based on passed in grid size"""
        if len(self.controller.import_orgainser) > 0:
            directory = askdirectory()
            if directory:
                self.progressbar = ttk.Progressbar(self, length=200, mode="indeterminate")
                self.progressbar.grid(column=0, row=5, sticky='NW')
                self.start_time = datetime.now()   
                self.progressbar.start()
                # main task
                t = Thread(target=lambda: self.pts_processor.process_files(directory, self.grid_size.get(), self.description.get(), self.survey_type.get()),)
                t.start()
                self.schedule_check(t)
        else:
            tk.messagebox.showerror(title='No Files Uploaded', message='Please upload PTS Files')

        
    def schedule_check(self, t):
        self.after(1000, self.check_if_done, t)

    def check_if_done(self, t):
        # If the thread has finished, re-enable the button and show a message.
        if not t.is_alive():
            self.progressbar.stop()
            self.progressbar.grid_remove()
            tk.messagebox.showinfo(title="Split Completed", message=f'Successful Split\nElasped Time: {self.round_seconds(datetime.now()-self.start_time)}')

        else:
            # Otherwise check again after one second.
            self.schedule_check(t)

    def round_seconds(self, time_delta):
        return time_delta - dt.timedelta(microseconds=time_delta.microseconds)
      
    def import_files(self):
        """Imports files to the list of imported files,
        after file has been imported, import tree structure is updated"""
        files = askopenfilenames(filetypes=self.ALLOWED_FILE_TYPES)
        if files:
            self.controller.import_orgainser.add_files(files)
            self.display_files()
    
    def display_files(self):
        """Displays the imported files in the tree"""
        for child in self.import_tree_display.winfo_children():
            child.destroy()

        self.active_file_vars = {}
        for f in self.controller.import_orgainser.imported_files:
                if isinstance(f, ImportedFile):
                    self._add_active_var(f)
                else:
                    self.display_unsuccessful_import(f)
        
        for row, f in enumerate(self.controller.import_orgainser):
            ttk.Checkbutton(self.import_tree_display, variable=self._get_active_var(f),
                onvalue=True, offvalue=False, command=f.file_active_toggle).grid(column=0, row=row, sticky='NW')
            ttk.Label(self.import_tree_display, text=f.file_name).grid(column=1, row=row, sticky='NW')

    def remove_files(self):
        """Removes the selected files from the project"""
        self.controller.import_orgainser.remove_non_active_files()
        self.display_files()

    def display_unsuccessful_import(self, file_name):
        tk.messagebox.showerror(
            title='Unsucessfull Import', 
            message=f'File "{os.path.basename(file_name)}"" already loaded into the project'
        )
    
    def _get_active_var(self, imported_file):
        """returns the active var for an imported file instance"""
        var = self.active_file_vars.get(imported_file)
        if not var:
            var = self._add_active_var(imported_file)
        return var

    def _add_active_var(self, imported_file):
        """adds the active varaible for a imported file 
        to the dictionary holding the active vars"""
        var = tk.BooleanVar(value=imported_file.file_active)
        self.active_file_vars[imported_file] = var
        return var





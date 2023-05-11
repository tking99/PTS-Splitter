from datetime import datetime
import datetime as dt
import tkinter as tk 
from tkinter import ttk
from tkinter.filedialog import askopenfilenames, askdirectory
from tkcalendar import Calendar, DateEntry
from threading import Thread

from models import ImportedFile
from processer import PTSFileProcessor


class GridSplitterDisplay(ttk.Frame):
    ALLOWED_FILE_TYPES = (('PTS', '.pts'), ('XYZ', '.xyz'), ('CSV', '.csv'), ('TXT', '.txt'))
    ALLOWED_POD_FILE_TYPE = (('POD', '.pod'), )
    GRID_OPTIONS = ('1000', '500', '100', '50', '20') 
    SURVEY_TYPES = ('AsBuilt', 'Topo')
    ISSUE_PURPOSE = ('FOR INFORMATION', 'ISSUED FOR HANDOVER')

    def __init__(self, controller, *args, **kwargs):
        super().__init__(controller, *args, **kwargs)
        self.controller = controller
        self.import_frame = ttk.Frame(self)
        self.import_frame.grid(column=0, row=0, sticky='NW')
        self.pts_processor = PTSFileProcessor(self.controller.import_orgainser, self.controller)

        ttk.Label(self.import_frame, text='Grid Splitter', font=("Arial", 12)).grid(column=0, row=0, padx=5, pady=5, sticky='NW')
        ttk.Label(self.import_frame, text='Step 1: Select ASCII Files to Split:').grid(column=0, row=1, padx=5, pady=5)
        ttk.Button(self.import_frame, text='Select', command=self.import_pts_files).grid(column=1, row=1, padx=5, pady=5)

        self.import_tree_display = ttk.Frame(self)
        self.import_tree_display.grid(column=0, row=1, sticky='NW', padx=5, pady=5)

        ttk.Separator(self, orient=tk.HORIZONTAL).grid(column=0, row=2, columnspan=10, sticky='ew')

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
        
        ttk.Separator(self, orient=tk.HORIZONTAL).grid(column=0, row=4, columnspan=10, sticky='ew')
        
        description_frame = ttk.Frame(self)
        description_frame.grid(column=0, row=5, sticky='NW')
        ttk.Label(description_frame, text='Step 3: Add Description').grid(column=0, row=0, padx=5, pady=5, sticky='NW') 

        self.description = tk.StringVar() 
        self.survey_type = tk.StringVar()
        ttk.Label(description_frame, text='Survey Description: ').grid(column=0, row=1, sticky='NW', pady=5, padx=5)
        ttk.Entry(description_frame, width=30, textvariable=self.description).grid(
            column=1, row=1, sticky='NW', pady=5, padx=5)
        ttk.Label(description_frame, text='Survey Type: ').grid(column=0, row=2, sticky='NW', pady=5, padx=5)
        survey_type_menu = ttk.OptionMenu(
            description_frame,
            self.survey_type,
            self.SURVEY_TYPES[0],
            *self.SURVEY_TYPES)
        survey_type_menu.grid(column=1, row=2, sticky='NW', pady=5, padx=5)

        ttk.Label(description_frame, text='Date of Survey: ').grid(column=0, row=3, sticky='NW', pady=5, padx=5)
        self.date_picker = DateEntry(description_frame, width=12, background='darkblue',
                    foreground='white', borderwidth=2)
        self.date_picker.grid(column=1, row=3, sticky='NW', pady=5, padx=5)
      
        ttk.Separator(self, orient=tk.HORIZONTAL).grid(column=0, row=6, columnspan=10, sticky='ew')
        
        self.export_frame = ttk.Frame(self)
        self.export_frame.grid(column=0, row=7, sticky='NW')
        ttk.Button(self.export_frame, text='SPLIT FILES', command=self.split,
            padding=(10,10)).grid(column=0, row=0, sticky='NW',
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
                t = Thread(target=lambda: self.pts_processor.process_pts_files(directory, self.grid_size.get(), self.description.get(), self.survey_type.get(),
                    self.date_picker.get_date()),)
                t.start()
                self.schedule_check(t)
        else:
            tk.messagebox.showerror(title='No Files Uploaded', message='Please upload ASCII Files')

        
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
      
    def import_pts_files(self):
        """Imports files to the list of imported files,
        after file has been imported, import tree structure is updated"""
        files = askopenfilenames(filetypes=self.ALLOWED_FILE_TYPES)
        if files:
            self.controller.import_orgainser.add_files(files)
            self.display_pts_files()

    def display_pts_files(self):
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




class PodExcellWritterDisplay(ttk.Frame):
    ALLOWED_POD_FILE_TYPE = (('POD', '.pod'), )
    ISSUE_PURPOSE = ('FOR INFORMATION', 'ISSUED FOR HANDOVER')

    def __init__(self, controller, *args, **kwargs):
        super().__init__(controller, *args, **kwargs)
        self.controller = controller

        pod_uploader_frame = ttk.Frame(self)
        pod_uploader_frame.grid(column=0, row=0, sticky='NW')
        ttk.Label(pod_uploader_frame, text='Pod Excel Uploader', font=("Arial", 12)).grid(column=0, row=0, sticky='NW', padx=5, pady=5)
        ttk.Label(pod_uploader_frame, text='Step 1: Select Pod Files to Upload:').grid(column=0, row=1, sticky='NW',
            padx=5, pady=5)
        ttk.Button(pod_uploader_frame, text='Select', command=self.import_pod_files).grid(column=1, row=1, padx=5, pady=5)
        self.import_pod_tree = ttk.Frame(pod_uploader_frame)
        self.import_pod_tree.grid(column=0, row=2, sticky='NW', padx=5, pady=5)
        ttk.Separator(self, orient=tk.HORIZONTAL).grid(column=0, row=1, columnspan=10, sticky='ew', pady=6)

        self.options_pod_frame = ttk.Frame(self)
        self.options_pod_frame.grid(column=0, row=2, sticky='NW')

        ttk.Label(self.options_pod_frame, text='Step 2: Add Attributes').grid(column=0, row=0, 
        padx=5, pady=5, sticky='NW')
        ttk.Label(self.options_pod_frame, text='Issue Purpose: ').grid(column=0, row=1, sticky='NW',
            padx=5, pady=5)

        self.issue_purpose = tk.StringVar()
        issue_type_menu = ttk.OptionMenu(
            self.options_pod_frame,
            self.issue_purpose,
            self.ISSUE_PURPOSE[0],
            *self.ISSUE_PURPOSE)
        issue_type_menu.grid(column=1, row=1, sticky='NW', pady=5, padx=5)

        ttk.Label(self.options_pod_frame, text='Drawn by: ').grid(column=0, row=2, sticky='NW',
            padx=5, pady=5)
        
        self.drawn_by = tk.StringVar()
        ttk.Entry(self.options_pod_frame, width=30, textvariable=self.drawn_by).grid(
            column=1, row=2, sticky='NW', pady=5, padx=5)

        ttk.Label(self.options_pod_frame, text='Drawn Date: ').grid(column=0, row=3, sticky='NW', pady=5, padx=5)
        self.date_picker = DateEntry(self.options_pod_frame, width=12, background='darkblue',
                    foreground='white', borderwidth=2)
        self.date_picker.grid(column=1, row=3, sticky='NW', pady=5, padx=5)
        
        ttk.Separator(self, orient=tk.HORIZONTAL).grid(column=0, row=3, columnspan=10, sticky='ew', pady=6)
        self.excel_frame = ttk.Frame(self)
        
        self.excel_frame.grid(column=0, row=4, sticky='NW')
        ttk.Label(self.excel_frame, text='Step 3: Select PW Excel File').grid(column=0, row=0, sticky='NW',
            padx=5, pady=5)
        ttk.Button(self.excel_frame, text='Select').grid(column=1, row=0, padx=5, pady=5)

        ttk.Separator(self, orient=tk.HORIZONTAL).grid(column=0, row=5, columnspan=10, sticky='ew', pady=6)
        
        self.export_frame = ttk.Frame(self)
        self.export_frame.grid(column=0, row=6, sticky='NW')
        ttk.Button(self.export_frame, text='UPLOAD TO EXCEL', padding=(10,10)).grid(column=0, row=0, sticky='NW',
            pady=20, padx=5)

    def _get_active_pod_var(self, imported_file):
        """returns the active var for an imported file instance"""
        var = self.active_pod_file_vars.get(imported_file)
        if not var:
            var = self._add_active_pod_var(imported_file)
        return var

    def _add_active_pod_var(self, imported_file):
        """adds the active varaible for a imported file 
        to the dictionary holding the active vars"""
        var = tk.BooleanVar(value=imported_file.file_active)
        self.active_pod_file_vars[imported_file] = var
        return var

    def remove_files(self):
        """Removes the selected files from the project"""
        self.controller.import_orgainser.remove_non_active_files()
        self.display_files()

    def display_unsuccessful_import(self, file_name):
        tk.messagebox.showerror(
            title='Unsucessfull Import', 
            message=f'File "{os.path.basename(file_name)}"" already loaded into the project')
    def display_pod_files(self):
        for child in self.import_pod_tree.winfo_children():
            child.destroy()

        self.active_pod_file_vars = {}
        for f in self.controller.import_pod_orgainser.imported_files:
                if isinstance(f, ImportedFile):
                    self._add_active_pod_var(f)
                else:
                    self.display_unsuccessful_import(f)
        
        for row, f in enumerate(self.controller.import_pod_orgainser):
            ttk.Checkbutton(self.import_pod_tree, variable=self._get_active_pod_var(f),
                onvalue=True, offvalue=False, command=f.file_active_toggle).grid(column=0, row=row, sticky='NW')
            ttk.Label(self.import_pod_tree, text=f.file_name).grid(column=1, row=row, sticky='NW')

    def import_pod_files(self):
        """imports pod files"""
        files = askopenfilenames(filetypes=self.ALLOWED_POD_FILE_TYPE)
        if files:
            self.controller.import_pod_orgainser.add_files(files)
            self.display_pod_files()

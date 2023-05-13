import os 
from pathlib import Path


class SubGrid:
    GRID_SIZE = ''
    NAME_PLACES = 0
    LEADING = False
  

    @classmethod
    def sub_grid_name(cls, x, y):
        """returns a string of the sub grid name"""
        if cls.LEADING:
            return f'{x[0:cls.NAME_PLACES]}{y[0:cls.NAME_PLACES]}'
        
        return f'{x[1:cls.NAME_PLACES]}{y[1:cls.NAME_PLACES]}'



class Grid500(SubGrid):
    GRID_SIZE = '500'
    NAME_PLACES = 4
    LEADING = True


class Grid100(SubGrid):
    GRID_SIZE = '100'
    NAME_PLACES = 4
    LEADING = False 


class Grid50(SubGrid):
    GRID_SIZE = '50'
    NAME_PLACES = 5 
    LEADING = False 


class Grid20(SubGrid):
    GRID_SIZE = '20'
    NAME_PLACES = 5
    LEADING = False


class WGrid:
    GRID_SIZE = '1000'
    GRIDS = {
        '500': Grid500,
        '100': Grid100,
        '50': Grid50,
        '20': Grid20
    }


    def __init__(self, name, lower_x, lower_y, upper_x, upper_y):
        self.name = name 
        self.lower_x = lower_x
        self.lower_y = lower_y
        self.upper_x = upper_x
        self.upper_y = upper_y
        self.grids = {} #sub grid: sub_grid

    def empty(self):
        """returns True is grid has no points"""
        return len(self.grids) == 0 
    
    def calculate_sub_grid(self, x, y, grid_size):
        grid_size = int(grid_size)
        delta_e = x - self.lower_x 
        delta_n = y - self.lower_y

        shift_e = int(delta_e / grid_size) * grid_size
        shift_n = int(delta_n / grid_size) * grid_size

        return (self.lower_x + shift_e, self.lower_y + shift_n) 


    def check_point(self, x, y):
        """returns a boolean if point lies within the grid"""
        if (x > self.lower_x and x < self.upper_x and y > self.lower_y and y < self.upper_y):
            return True
        else :
            return False

    def __str__(self):
        return self.name 

    def __repr__(self):
        return self.name
      

class ImportedFile:
    def __init__(self, file_path):
        self.path = Path(file_path)
        self.file_active = True 

    @property 
    def exists(self):
        return self.path.exists()
  
    @property
    def file_name(self):
        """returns the file name of the imported file
        if the path exists"""
        if self.exists:
            return os.path.basename(self.path)

    @property
    def normpath(self):
        return os.path.normpath(self.path)

    @property 
    def directory(self):
        """returns the directory path of the imported file
        if the path exists"""
        if self.exists:
           return os.path.dirname(self.path)

    def file_active_toggle(self):
        """toggles the state of file active"""
        self.file_active = not self.file_active
        
    def __str__(self):
        return self.file_name 

    def __repr__(self):
        return self.file_name


class ImportedFileOrgainser: 
    def __init__(self):
        # holds a list of paths 
        self.imported_files = []

    def is_empty(self):
        """Returns a boolean if the imported 
        file orgainser is empty"""
        return len(self.imported_files) == 0 

    def add_files(self, file_paths):
        """returns a list of imported files"""
        return [self.add_file(f) for f in file_paths]
      
    def add_file(self, file_path):
        """returns a single imported file"""
        if not self.check_path_exists(file_path):
            imported_file = ImportedFile(file_path)
            self.imported_files.append(imported_file)
            return imported_file
        return file_path

    def remove_non_active_files(self):
        self.imported_files = [f for f in self.imported_files 
            if not f.file_active]
            
    def remove_file(self, file_path):
        if self.check_path_exists(file_path):
            self.imported_files.remove(file_path)
      
    def check_path_exists(self, file_path):
        for f in self.imported_files:
            if os.path.normpath(file_path) == f.normpath:
                return True 
        return False

    def __iter__(self):
        for f in self.imported_files:
            yield f

    def __len__(self):
        return sum(1 for f in self.imported_files if f.file_active)
import os
from models import WGrid, Grid500, Grid100, Grid50, Grid20

class PTSFileProcessor:
    GRIDS = {'1000': WGrid,
        '500': Grid500,
        '100': Grid100,
        '50': Grid50,
        '20': Grid20}

    def __init__(self, import_orgainser, controller):
        self.import_orgainser = import_orgainser
        self.controller = controller
     
    def process_files(self, directory, grid_size, description, survey_type): 
        count = {}
        GRID_CLASS = self.GRIDS[grid_size]
        for imported_file in self.import_orgainser:
            if imported_file.exists and imported_file.file_active:
                with open(imported_file.path, 'r', encoding='utf-8-sig') as infile:
                    for line in infile:
                        s = line.split()
                        if len(s) > 2:
                            e, n = float(s[0]), float(s[1])
                            wgrid = self.controller.get_wgrid(e,n)
                            if grid_size != '1000':
                                grid_cords = wgrid.calculate_sub_grid(e, n, grid_size)
                            else:
                                grid_cords = (wgrid.lower_x, wgrid.lower_y)
                            if grid_cords not in count:
                                count[grid_cords] = 1
                            else:
                                count[grid_cords] += 1 
        try:
            outfiles = {}
            file_num = 1
            for imported_file in self.import_orgainser:
                if imported_file.exists and imported_file.file_active:
                    with open(imported_file.path, 'r', encoding='utf-8-sig') as infile:               
                        for line in infile:
                            s = line.split()
                            if len(s) > 2:
                                e, n = float(s[0]), float(s[1])
                                wgrid = self.controller.get_wgrid(e,n)
                                if grid_size != '1000':
                                    grid_cords = wgrid.calculate_sub_grid(e, n, grid_size)
                                    file_name = f'HS2-{wgrid.name}-{GRID_CLASS.sub_grid_name(str(grid_cords[0]),str(grid_cords[1]))}-{description}'  
                                else:
                                    grid_cords = (wgrid.lower_x, wgrid.lower_y)
                                    file_name = f'HS2-{wgrid.name}-{description}'
                                    
                                if grid_cords not in outfiles:
                                    file_name += f'({file_num}of{len(count)})-{survey_type}.pts'
                                    file_name = os.path.join(directory, file_name)
                                    outfiles[grid_cords] = open(file_name, 'w')
                                    outfiles[grid_cords].write(str(count[grid_cords])+ '\n')
                                    file_num += 1
                                outfiles[grid_cords].write(self.get_line(s))
                    
        finally:
            for outfile in outfiles.values():
                outfile.close()

    def get_line(self, s):
        line = ''
        for l in s: 
            line += l + ' '
        line += '\n'
        return line 
                         

    def check_pts_line(self, pts_line):
        if len(pts_line) > 2:
            return True 
        return False   
                 
    
class GridCreator:
    GRIDS = {'1000': WGrid,
        '500': Grid500,
        '100': Grid100,
        '50': Grid50,
        '20': Grid20}

    def __init__(self, grid_size):
        self.GRID_CLASS = self.GRIDS.get(grid_size)
        self.grid_files = {}  #{} WGrid: {(EN Lower left corder ):File name}}


    def get_sub_grid_file(self, wgrid, e, n):
        """passed in wgrid and lower left e n of sub grid"""
        grid = self.grid_files.setdefault(wgrid, {})
        return grid.setdefault((e, n), open(f'HS2-{wgrid.name}-{self.GRID_CLASS.sub_grid_name(str(e),str(n))}.pts', 'w'))

    def get_w_grid_file(self, wgrid):
        grid = self.grid_files.setdefault(wgrid, {})
        return grid.setdefault((wgrid.lower_x, wgrid.lower_y), open(f'HS2-{wgrid.name}.pts', 'w'))

    
    def close_grid_files(self):
        for v in self.grid_files.values():
            for f in v.values():
                f.close()
       

    



    

        
       

        


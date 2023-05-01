from models import WGrid

class GridImporter:
    @staticmethod
    def read(file_name):
        grids = []
        with open(file_name, 'r', encoding='utf-8-sig') as f:
            lines = f.read().splitlines()
            for l in lines:
                g = l.split(',')
                grids.append(WGrid(
                    g[0],
                    float(g[1]),
                    float(g[2]),
                    float(g[3]),
                    float(g[4])))
        return grids 
            
          




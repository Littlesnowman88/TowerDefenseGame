__path_manager = None
def getPathManager():
    from PathClass import Path
    import random
    class PathManager:
        def __init__(self):
            self._grid = None
            self._CANVAS_DIM = 600
            self._SQUARE_SIZE = 30
            self._NUM_CELLS_PER_DIM = int(self._CANVAS_DIM / self._SQUARE_SIZE)
            self._minimum_path_length = 20
            self._all_paths_file_name = "paths/all_paths.txt"
            self._paths = []


        def getCanvasDim(self): return self._CANVAS_DIM
        def getCellSize(self): return self._SQUARE_SIZE
        def getNumCellsPerDim(self): return self._NUM_CELLS_PER_DIM
        def setGrid(self, grid): self._grid = grid
        def getRandomPath(self):
            return self._paths[random.randint(0, (len(self._paths) - 1))]
        def getPathEndCellCoords(self): return self._paths[0].get_cell(len(self._paths[0])-1).getCenter()
        def getPathCopy(self, path):
            cell_list = path.get_path_copy()
            path_copy = Path(600/30)
            for cell in cell_list:
                path_copy.add_cell(cell)
            return path_copy

        def initializeMap(self):
            self._paths = []
            self.readPaths()
            self.verifyPaths()

        def readPaths(self):
            with open("paths/all_paths.txt") as allpaths:
                for elem in allpaths:
                    self._paths.append(self.readPathInfo(elem.strip()))

        def readPathInfo(self, path_name):
            '''Read path information from a file and create a path object for it.'''
            path = Path(self._NUM_CELLS_PER_DIM)
            with open("paths/%s" % path_name) as pf:
               # print("Reading from paths/%s..." % path_name)         #USE THIS FOR PATH-READING DEBUGGING
                for elem in pf:
                    elem = elem.strip()
                    x, y = map(int, elem.split(','))  # map(int) to make ints.
                    path.add_cell(self._grid[y][x])
                    self._grid[y][x].set_type('path')
            return path


        def verifyPaths(self):
            self.verifyPathEndingsAndLengths()
            self.verifyAvailableCells()

        def verifyPathEndingsAndLengths(self):
            '''All paths need to end at the same spot: the home base!'''
            control_path_final_cell = self._paths[0].get_cell(len(self._paths[0]) - 1)
            for path in self._paths:
                if path.get_cell(len(path) - 1).getCenter() != control_path_final_cell.getCenter():
                    raise IOError("Not all paths have ended in the same spot!")
                if len(path) < self._minimum_path_length:
                    raise IOError("Not all paths are long enough! Minimum required length: %d" % self._minimum_path_length)

        def verifyAvailableCells(self):
            path_cell_count = 0
            unoccupied_cell_count=0
            for row in self._grid:
                for cell in row:
                    if cell.get_type() == "path": path_cell_count += 1
                    else: unoccupied_cell_count += 1
            if (path_cell_count / unoccupied_cell_count) >= 1:
                raise IOError("less than 50 percent of the cells may be path cells.")


    global __path_manager
    if __path_manager == None:
        __path_manager = PathManager()
    return __path_manager

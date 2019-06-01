from CellClass import *
class Path:
    '''Define a sequence of Cells from one edge of the board
    to the other, on which the invaders will walk.
    '''

    def __init__(self, grid_size):
        # 0th item is cell where the invaders start.  Last item
        # is where they exit the board.

        # grid_size is the size of the board.  Used to check that a path
        # starts and ends on an edge.

        self._path = []
        self._grid_size = grid_size

    def add_cell(self, cell):
        assert isinstance(cell, Cell)
        if self._path == []:
            # empty list, so check that cell is on the edge.
            assert cell.get_x() == 0 or cell.get_x() == self._grid_size - 1 or \
                   cell.get_y() == 0 or cell.get_y() == self._grid_size - 1
        else:
            # Verify that the cell is adjacent to the last cell in the path.
            last_cell = self._path[-1]
            # Need to be adjacent horizontally or vertically -- not just diagonal.
            assert cell.get_x() == last_cell.get_x() or cell.get_y() == last_cell.get_y()
            assert abs(cell.get_x() - last_cell.get_x()) <= 1 and \
                   abs(cell.get_y() - last_cell.get_y()) <= 1

        self._path.append(cell)

    def get_path_copy(self):
        path_copy = []
        for cell in self._path:
            path_copy.append(cell)
        return path_copy

    def remove_cell(self, cell):
        self._path.remove(cell)

    def __len__(self):
        return len(self._path)

    def get_cell(self, idx):
        return self._path[idx]

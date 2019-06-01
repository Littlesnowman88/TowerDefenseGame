import random
from TowerAbstractFactory import *
from HomeBase import *
class Cell():
    TYPE2COL = { 'path': '#d1ae77', 'tower': 'white', 'other': 'white' }
    # This variable stores a state corresponding to the type of tower to place on click
    #   (not a great name for it, but couldn't think of anything better at the moment)
    towerType = "blue"  # default to placing a blue circle tower
    tower_cost = BlueCircleTower._build_price

    def __init__(self, canvas, x, y, size, type='other'):
        self._canvas = canvas
        self._x = x
        self._y = y
        self._size = size
        self._ulx = x * size          # upper-left x
        self._lrx = self._ulx + size  # lower-right x
        self._uly = y * size          # upper-left y
        self._lry = self._uly + size  # lower-right y
        self._tag = "cell" + str(x) + str(y)
        self._id = None
        self._tower = None
        self._homebase = getHomeBase()
        self._tower_factory = getTowerAbstractFactory()
        # True when the mouse is in this cell.
        self._mouseIn = False
        self.set_type(type)
        self._id = self._canvas.create_rectangle(self._ulx, self._uly, self._lrx, self._lry,
                                               fill=Cell.TYPE2COL[self._type], tag=self._tag)
        self._canvas.tag_bind(self._id, "<Enter>", self.highlight)
        self._canvas.tag_bind(self._id, "<Leave>", self.clear)

        self._observerList = []
        self._changed = False

        ######################
        #    KEY BINDINGS    #
        ######################
        self._canvas.bind_all('b', self.setTowerTypeToBlue)
        self._canvas.bind_all('r', self.setTowerTypeToRed)
        self._canvas.bind_all('g', self.setTowerTypeToGreen)
        self._canvas.tag_bind(self._id, "<Button-1>", self.callBuildTower)
        self._canvas.tag_bind(self._id, "<Shift-Button-1>", self.callDeleteTower)

    def setTowerTypeToBlue(self, event):
        Cell.towerType = "blue"
        Cell.tower_cost = BlueCircleTower._build_price

    def setTowerTypeToRed(self, event):
        Cell.towerType = "red"
        Cell.tower_cost = RedSquareTower._build_price

    def setTowerTypeToGreen(self, event):
        Cell.towerType = "green"
        Cell.tower_cost = GreenDiamondTower._build_price

    def clear(self, event=None):
        self._mouseIn = False
        self._canvas.itemconfig(self._id, fill=Cell.TYPE2COL[self._type])

    def highlight(self, event=None):
        # Show green where the mouse is.
        self._canvas.itemconfig(self._id, fill='green')
        self._mouseIn = True

    def __contains__(self, xy):
        '''Return True if the given x,y tuple is in the rectangle, False
        otherwise.'''
        x, y = xy
        return self._ulx < x < self._lrx and self._uly < y < self._lry

    def get_x(self):
        return self._x
    def get_y(self):
        return self._y
    def get_size(self):
        return self._size

    def getCenter(self):
        return (self.get_center_x(), self.get_center_y())

    def get_center_x(self):
        return self._ulx + (self._size / 2)
    def get_center_y(self):
        return self._uly + (self._size / 2)

    def has_tower(self):
        if self._tower == None:
            return False
        return True

    def set_type(self, type):
        assert type in ('path', 'tower', 'other')
        self._type = type     # should use sub-class?
        if (self._id is not None and self._type != 'tower'):
            self._canvas.itemconfig(self._id, fill=Cell.TYPE2COL[self._type])
    def get_type(self):
        return self._type

    def callBuildTower(self, event):
        if (self._type != 'path' and self._type != 'tower'):
            self._tower_factory.createTower(self._canvas, self)

    def callDeleteTower(self, event):
        if (self._type == 'tower'):
            self._tower.callDelete(event)

    def __delete__(self):
        self._canvas.delete(self._id)
        del self
from TowerClasses import *
from HomeBase import *
__tower_abstract_factory = None
def getTowerAbstractFactory():
    class TowerAbstractFactory():
        def __init__(self):
            self._homebase = getHomeBase()
        def createTower(self, canvas, cell):
            if cell.towerType == "blue":
                try:
                    self._homebase.subtractGold(cell.tower_cost)
                    cell._tower = BlueCircleTower(canvas, cell)
                except RuntimeError: print("InsufficientFunding for a BlueCircleTower!")

            elif cell.towerType == "red":
                try:
                    self._homebase.subtractGold(cell.tower_cost)
                    cell._tower = RedSquareTower(canvas, cell)
                except RuntimeError: print("InsufficientFunding for a RedSquareTower!")

            elif cell.towerType == "green":
                try:
                    self._homebase.subtractGold(cell.tower_cost)
                    cell._tower = GreenDiamondTower(canvas, cell)
                except RuntimeError:
                    print("InsufficientFunding for a GreenDiamondTower!")
            else: raise TypeError

    global __tower_abstract_factory
    if __tower_abstract_factory == None:
        __tower_abstract_factory = TowerAbstractFactory()
    return __tower_abstract_factory
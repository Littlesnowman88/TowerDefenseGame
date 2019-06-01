# imports go here
from tkinter import PhotoImage

__homebase = None

def getHomeBase():
    from interface import implements
    from Subject_Observer import Subject
    class HomeBase(implements(Subject)):
        def __init__(self):
            self._position = None
            self._x = None
            self._y = None
            self._health = 550
            self._alive = True
            self._gold = 100
            self._canvas = None
            self._id = None
            self._image = PhotoImage(file="images/castleGate-turned.gif")
            self._observers = []
            self._changed = False

        def setCanvas(self, canvas):
            self._canvas = canvas
        def setPosition(self, pos):
            self._position = pos
            self._x, self._y = pos
        # we'll need this function if we want to have invaders target the HomeBase
        def getCenter(self):
            return self._position
        def getHealth(self):
            return self._health
        def isAlive(self):
            return self._alive
        def getGold(self):
            return self._gold
        def addGold(self, gold):
            self._gold += abs(gold)
            self.setChanged()
        def subtractGold(self, gold):
            if self._gold - abs(gold) < 0:
                raise RuntimeError("Gold may not be less than zero.")
            else:
                self._gold -= abs(gold)
                self.setChanged()

        def takeDamage(self, damage):
            self._health -= damage
            if self._health <= 0: self._alive = False
            self.setChanged()

        def render(self):
            if self._id == None:    # it's a Singleton, so safeguard against accidentally rendering more than one
                self._id = self._canvas.create_image(self._x + 5, self._y, image=self._image)

        def __delete__(self):
            self._canvas.delete(self._id)
            del self

        '''Home base as a subject of App'''
        def registerObserver(self, observer): self._observers.append(observer)
        def removeObserver(self, observer): self._observers.remove(observer)
        def removeAllObservers(self): self._observers = []
        def isChanged(self): return self._changed
        def setChanged(self):
            self._changed = True
            self.notifyObservers()
        def notifyObservers(self):
            if self.isChanged():
                for observer in self._observers:
                    observer.update(self)
            self._changed = False



# stuff below here is just Singleton pattern stuffs - ignore ;P
    global __homebase
    if __homebase == None:
        __homebase = HomeBase()
    return __homebase


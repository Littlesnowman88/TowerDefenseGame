from MoveBehavior import *
from ShapeRendering import *
from tkinter import PhotoImage
from Subject_Observer import Subject, Observer
from interface import implements
from TargetMediator import *

class AbstractProjectile(implements(Subject), implements(Observer)):
    def __init__(self, canvas, shooter_position, distance=None, target_object=None, target_position = None):
        self._canvas = canvas
        self._speed = None
        self._damage = None
        self._position = shooter_position
        self._x, self._y = self._position
        self._distance = distance
        self._target_object = target_object
        self._target_position = target_position
        self._moveBehavior = None
        self._shape = None
        self._id = None
        self._alive = True
        self._changed = False
        self._observers = []
        self._target_mediator = getTargetMediator()
        self._target_mediator.addProjectile(self)

    def render(self):
        if self._target_object != None: self.renderToObject()
        else: self.renderToPosition()

    def renderToObject(self):
        if (self._target_object != None):
            #sometimes the target dies and removes all observers before this hs a chance to see
            self._moveBehavior.move()
            if self._moveBehavior.isMoving():
                self.renderShape()
                self._canvas.after(30, self.renderToObject)
            else:
                self.evaluatePosition()

    def renderToPosition(self):
        self._moveBehavior.move()
        if self._moveBehavior.isMoving():
            self.renderShape()
            self._canvas.after(30, self.renderToPosition) #after milliseconds, repeat this function
        else:
            self.evaluatePosition()

    def renderShape(self):
        self._shape.assignShapeXY(self._moveBehavior.getCenter())
        self._shape.render()

    def isAlive(self):
        return self._alive

    def evaluatePosition(self):
        if self._moveBehavior.isAtTarget():
            if self._target_object != None:
                self.attackTarget()
        self.__delete__()

    def attackTarget(self):
        self._target_object.takeDamage(self._damage)
        #TODO: MAYBE RENDER AN EXPLOSION HERE?

    def __delete__(self):
        self._alive = False
        self._moveBehavior.stopMoving()
        self._shape.__delete__()

        # self._target_mediator.removeProjectile(self)
        del self

    '''Projectile as a Subject of its shooter'''
    def registerObserver(self, observer): self._observers.append(observer)
    def removeObserver(self, observer): self._observer.remove(observer)
    def removeAllObservers(self): self._observers = []
    def isChanged(self): return self._changed
    def setChanged(self):
        self._changed = True
        self.notifyObservers()
    def notifyObservers(self):
        for observer in self._observers:
            observer.update(self)

    '''Projectile as an observer of its target'''
    def update(self, changed_thing):
        if not changed_thing.isAlive():
            self._target_object = None
            self.__delete__()
        if changed_thing.getHasMoved():
            self.setTargetCoordinates(changed_thing.getCenter())

    def setTargetCoordinates(self, position):
        # self._target_position = position
        self._moveBehavior.set_target_position(position)


class SamplePositionProjectile(AbstractProjectile):
    def __init__(self, canvas, shooter_position):
        AbstractProjectile.__init__(self, canvas, shooter_position)
        self._damage = 10
        self._size = 4
        self._color = 'black'
        self._speed = 1.5
        self._target_position = (400, 300)
        self._moveBehavior = TowardsTargetPosition(self._speed, self._position, self._target_position)
        self._shape = DiamondRendering(self._canvas, self._position, self._size, self._color)
        self.render()

class HomingArrow(AbstractProjectile):
    def __init__(self, canvas, shooter_position, target_object):
        AbstractProjectile.__init__(self, canvas, shooter_position, target_object=target_object)
        self._damage = 10
        self._image = PhotoImage(file = "images/pixelArtArrow-10px.gif")
        self._shape = ImageRendering(self._canvas, self._position, self._image)
        self._speed = 4
        self._moveBehavior = TowardsTargetObject(self._speed, self._target_object, self._position)
        self.render()

class HomingFireball(AbstractProjectile):
    def __init__(self, canvas, shooter_position, target_object):
        AbstractProjectile.__init__(self, canvas, shooter_position, target_object=target_object)
        self._damage = 6
        self._burn_damage = 3
        self._burn_duration = 20 #number of moves or 30-millisecond refreshes
        self._image = PhotoImage(file = "images/fireball.gif")
        self._shape = ImageRendering(self._canvas, self._position, self._image)
        self._speed = 2.5
        self._moveBehavior = TowardsTargetObject(self._speed, self._target_object, self._position)
        self.render()

    def attackTarget(self):
        if self._target_object != None:
            self._target_object.takeDamage(self._damage)
        if self._target_object != None:
            self._target_object.setBurned(self._burn_duration, self._burn_damage)



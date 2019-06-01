from ShapeRendering import *
from TargetMediator import *
from HomeBase import *
from ProjectileClasses import *
from Subject_Observer import Subject, Observer
import types, random


##########################################
#          ABSTRACT TOWER CLASS          #
##########################################
class AbstractTower(implements(Subject), implements(Observer)):
    _build_price = None
    def __init__(self, canvas, cell):
        self._canvas = canvas
        self._cell = cell
        self._x, self._y = self._cell.getCenter()
        self._cell.set_type('tower')
        self._health = None
        self._sell_price = None
        self._size = None
        self._color = None
        self._shape = None
        self._burn_shape = None
        self._health_bar = None
        self._projectile = None
        self._shoot_delay = None #IN MILLISECONDS
        self._range_factor = None
        self._coordsInRange = None
        self._alive = True
        self._shooting = False
        self._changed = False
        self._observers = []
        self._active_invaders = []
        self._invaders_in_range = []
        self._shooting_thread = None
        self._target_mediator = getTargetMediator()
        self._target_mediator.addTower(self)
        self.registerObserver(self._target_mediator)
        self._homebase = getHomeBase()


    def getCenter(self): return (self._x, self._y)
    def isAlive(self): return self._alive
    def isShooting(self): return self._shooting

    '''Render functions'''
    def render(self):
        self.renderShape()
        self.renderHealthBar()

    def renderShape(self):
        self._shape.assignShapeXY(self._cell.getCenter())
        self._shape.render()
    def renderHealthBar(self):
        self._health_bar.assignShapeXY(self._shape.getBottomLeftCorner())
        self._health_bar.render()

    '''Dealing with invaders'''
    def addActiveInvader(self, invader): self._active_invaders.append(invader)
    def removeActiveInvader(self, invader):  self._active_invaders.remove(invader)
    def takeDamage(self, damage):
        self._health -= damage
        self._health_bar.subtractHealth(damage)
        if self._health <= 0:
            self.__delete__()

    def setBurned(self, burn_duration, burn_damage):
        self._burn_duration = burn_duration
        self.handleBurn(burn_damage)
    def handleBurn(self, burn_damage):
        if (self._burn_duration > 0) and (self.isAlive()):
            self._burn_duration -= 1
            self._burn_shape.unrender()
            self._burn_shape.assignShapeXY(self.getCenter())
            self._burn_shape.render()
            self._canvas.after(30, self.handleBurn, burn_damage)
        else: self._burn_shape.unrender()



    def callDelete(self, event):
        '''USED WHEN THE TOWER IS CLICKED ON WITH THE CANVAS-ASSIGNED DELETE BUTTON.'''
        self._homebase.addGold(self._sell_price)
        self.__delete__()

    def quickDelete(self):
        self._alive = False
        self._invaders_in_range = []
        self._shooting = False
        self._shape.__delete__()
        self._burn_shape.__delete__()
        self._health_bar.__delete__()
        del self

    def __delete__(self):
        '''MAKE THE CELL NOTICE THAT THE TOWER IS DESTROYED with subject observer pattern perhaps. You did it wrong here.'''
        self._alive = False
        self._invaders_in_range = []
        self._shooting = False
        self.setChanged()
        self._cell.set_type('other')
        self._shape.__delete__()
        self._burn_shape.__delete__()
        self._health_bar.__delete__()
        self.removeAllObservers()
        del self

    '''shooting methods'''
    def initializeProjectile(self):
        raise RuntimeError
    def startShooting(self):
        if not self.isShooting():
            self._shooting = True
            self.shoot()
    def stopShooting(self):
        if len(self._invaders_in_range) == 0:
            self._shooting = False
    def shoot(self):
        if (len(self._invaders_in_range) > 0) and self.isAlive():
            #create the projectile and register it as an observer of an invader
            target_invader_id = random.randint(0, (len(self._invaders_in_range) - 1))
            self._invaders_in_range[target_invader_id].registerObserver(self._projectile(
                self._canvas, self.getCenter(), self._invaders_in_range[target_invader_id]))
            self._canvas.after(self._shoot_delay, self.shoot)
        else: self.stopShooting()


    '''Range Functions'''
    def getCoordsInRange(self, range_factor):
        minX = self._x - (range_factor * self._cell._size)  # min x-coord
        minY = self._y - (range_factor * self._cell._size)  # min y-coord
        maxX = self._x + (range_factor * self._cell._size)  # max x-coord
        maxY = self._y + (range_factor * self._cell._size)  # max y-coord

        coordRange = [minX, maxX, minY, maxY]
        return coordRange

    def isInRange(self, invaderX, invaderY):
        if (self._coordsInRange[0] <= invaderX <= self._coordsInRange[1]) and (
                self._coordsInRange[2] <= invaderY <= self._coordsInRange[3]):
            return True
        return False

    '''Subject-Related Functions'''
    def getHasMoved(self): return False #NO TOWERS MOVE. EVER. (Projectiles need this information, though)
    def registerObserver(self, observer): self._observers.append(observer)
    def removeObserver(self, observer): self._observers.remove(observer)
    def removeAllObservers(self): self._observers = {}
    def setChanged(self):
        self._changed = True
        self.notifyObservers()
    def notifyObservers(self):
        if self.isChanged():
            for observer in self._observers:
                observer.update(self)
    def isChanged(self): return self._changed

    '''Observer-Related Functions'''
    def update(self, changed_thing):
        if isinstance(changed_thing, AbstractInvader):
            self.processChangedInvader(changed_thing)
        else: raise TypeError

    def processChangedInvader(self, changed_invader):
        if not changed_invader.isAlive():
            if changed_invader in self._invaders_in_range:
                    self._invaders_in_range.remove(changed_invader)
                    self.stopShooting()
        elif changed_invader._moveBehavior.getHasMoved():
            inv_x, inv_y = changed_invader.getCenter()
            if self.isInRange(inv_x, inv_y):
                if changed_invader not in self._invaders_in_range:
                    self._invaders_in_range.append(changed_invader)
                    self.startShooting()
            elif changed_invader in self._invaders_in_range:
                self._invaders_in_range.remove(changed_invader)
                self.stopShooting()


##########################################
#        BLUE CIRCLE TOWER CLASS         #
##########################################
class BlueCircleTower(AbstractTower):
    _build_price = 10
    def __init__(self, canvas, cell):
        AbstractTower.__init__(self, canvas, cell)
        self._health = 100
        self._sell_price = 5
        self._size = 4
        self._color = "#3030e0"
        self._shoot_delay = 500
        self._range_factor = 1.5
        self._coordsInRange = self.getCoordsInRange(self._range_factor)
        self._projectile = HomingArrow
        self._shape = CircleRendering(self._canvas, self._cell.getCenter(),
                                                self._size, self._color)
        self._burn_shape = BurnRendering(self._canvas, self._cell.getCenter())
        self._health_bar = HealthBarRendering(self._canvas, self._health, self._shape.getBottomLeftCorner(),
                                                        self._shape.getRightmostPoint())
        self.render()
        self._canvas.tag_bind(self._shape._id, "<Shift-Button-1>", self.callDelete)


##########################################
#         RED SQUARE TOWER CLASS         #
##########################################
class RedSquareTower(AbstractTower):
    _build_price = 35
    def __init__(self, canvas, cell):
        AbstractTower.__init__(self, canvas, cell)
        self._health = 300
        self._sell_price = 14
        self._size = 6
        self._color = "#ad0020"
        self._shoot_delay = 500
        self._range_factor = 2.5
        self._coordsInRange = self.getCoordsInRange(self._range_factor)
        self._projectile = HomingFireball
        self._shape = SquareRendering(self._canvas, self._cell.getCenter(),
                                               self._size, self._color)
        self._burn_shape = BurnRendering(self._canvas, self._cell.getCenter())
        self._health_bar = HealthBarRendering(self._canvas, self._health, self._shape.getBottomLeftCorner(),
                                              self._shape.getRightmostPoint())

        self.render()
        self._canvas.tag_bind(self._shape._id, "<Shift-Button-1>", self.callDelete)


##########################################
#        GREEN DIAMOND TOWER CLASS       #
##########################################
class GreenDiamondTower(AbstractTower):
    _build_price = 60
    def __init__(self, canvas, cell):
        AbstractTower.__init__(self, canvas, cell)
        self._health = 450
        self._sell_price = 25
        self._size = 12
        self._color = "#00ad22"
        self._shoot_delay = 500
        self._range_factor = 3.5
        self._coordsInRange = self.getCoordsInRange(self._range_factor)
        self._projectile = HomingArrow
        self._shape = DiamondRendering(self._canvas, self._cell.getCenter(),
                                                   self._size, self._color)
        self._burn_shape = BurnRendering(self._canvas, self._cell.getCenter())
        self._health_bar = HealthBarRendering(self._canvas, self._health, self._shape.getBottomLeftCorner(),
                                              self._shape.getRightmostPoint())


        self.render()
        self._canvas.tag_bind(self._shape._id, "<Shift-Button-1>", self.callDelete)





#KEEP THESE IMPORTS AT THE BOTTOM OF THE FILE
from InvaderClasses import AbstractInvader

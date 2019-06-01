from tkinter import PhotoImage
from ShapeRendering import *
from MoveBehavior import *
from WaveManager import *
from HomeBase import *
from TargetMediator import *
from ProjectileClasses import *
from Subject_Observer import Subject, Observer
import types, random
from TowerClasses import AbstractTower

##########################################
#            ABSTRACT INVADER            #
##########################################
class AbstractInvader(implements(Subject), implements(Observer)):
    def __init__(self, canvas, path):
        self._canvas = canvas
        self._path = path
        self._cell_size = self._path.get_cell(0)._size #used in calculating range
        self._health = None
        self._damage = None
        self._speed = None
        self._burn_duration = 0
        self._damage_from_burns = 0
        self._gold_prize = None
        self._size = None
        self._color = None
        self._shape = None
        self._burn_shape = None
        self._health_bar = None
        self._moveBehavior = None
        self._projectile = None
        self._shoot_delay = None #IN SECONDS
        self._range_factor = None
        self._coordsInRange = None
        self._alive = True
        self._shooting = False
        self._can_shoot = False
        self._changed = False
        self._observers = []
        self._active_towers = []
        self._towers_in_range = []
        self._target_mediator = getTargetMediator()
        self._target_mediator.addInvader(self)
        self.registerObserver(self._target_mediator)
        self._homebase = getHomeBase()

    def getCenter(self): return (self._moveBehavior.getCenter())
    def canShoot(self): return self._can_shoot
    def isShooting(self): return self._shooting
    def isAlive(self): return self._alive

    '''rendering and movement-related methods'''
    def render(self):
        if self.isAlive():
            self._moveBehavior.move() #move the invader
            if self._moveBehavior.isMoving():
                self.renderShape()
                self.renderHealthBar()
                self.checkHasMoved()
                self._canvas.after(30, self.render) #after milliseconds, repeat this function
            else:
                self.evaluatePosition()

    def renderShape(self):
        self._shape.assignShapeXY(self._moveBehavior.getCenter())
        self._shape.render()
    def renderHealthBar(self):
        self._health_bar.assignShapeXY(self._shape.getBottomLeftCorner())
        self._health_bar.render()
    def checkHasMoved(self):
        if self.getHasMoved():
            self.setChanged()
            self._moveBehavior.clearHasMoved()
            if self.canShoot(): self.searchForTowers()
    def getHasMoved(self):
        return self._moveBehavior.getHasMoved()
    def evaluatePosition(self):
        if self._moveBehavior.isAtTarget():
            self._homebase.takeDamage(self._damage)
            self.__delete__()
        else:
            self.__delete__() #FIXMEFIXME get rid of this delete if you ever stop an invader when it is not at its target

    '''dealing with towers'''
    def takeDamage(self, damage):
        self._health -= damage
        self._health_bar.subtractHealth(damage)
        if self._health <= 0:
            self._homebase.addGold(self._gold_prize)
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




    '''Self-Deletion Methods'''
    def quickDelete(self):
        self._alive = False
        self._moveBehavior._isMoving = False
        self._towers_in_range = []
        self._shooting = False
        self._shape.__delete__()
        self._burn_shape.__delete__()
        self._health_bar.__delete__()
        del self

    def __delete__(self):
        self._alive = False
        self._towers_in_range = []
        self._shooting = False
        self.setChanged()
        self.removeAllObservers()
        self._shape.__delete__()
        self._burn_shape.__delete__()
        self._health_bar.__delete__()
        del self

    def addActiveTower(self, tower): self._active_towers.append(tower)
    def removeActiveTower(self, tower): self._active_towers.remove(tower)
    def searchForTowers(self):
        for tower in self._active_towers:
            tower_x, tower_y = tower.getCenter()
            self._coordsInRange = self.getCoordsInRange(self._range_factor)
            if self.IsInRange(tower_x, tower_y):
                if tower not in self._towers_in_range:
                    self._towers_in_range.append(tower)
                    self.startShooting()
            elif tower in self._towers_in_range:
                self._towers_in_range.remove(tower)
                self.stopShooting()

    '''Range Functions'''
    def getCoordsInRange(self, range_factor):
        self._x, self._y = self._moveBehavior.getCenter()
        minX = self._x - (range_factor * self._cell_size)  # min x-coord
        minY = self._y - (range_factor * self._cell_size)  # min y-coord
        maxX = self._x + (range_factor * self._cell_size)  # max x-coord
        maxY = self._y + (range_factor * self._cell_size)  # max y-coord

        coordRange = [minX, maxX, minY, maxY]
        return coordRange

    def IsInRange(self, towerX, towerY):
        if (self._coordsInRange[0] <= towerX <= self._coordsInRange[1]) and (
                self._coordsInRange[2] <= towerY <= self._coordsInRange[3]):
            return True
        else:
            return False

    '''shooting methods'''
    def initializeProjectile(self):
        raise RuntimeError
    def startShooting(self):
        if not self.isShooting():
            self._shooting = True
            self.shoot()
    def stopShooting(self):
        if len(self._towers_in_range) == 0:
            self._shooting = False
    def shoot(self):
        if (len(self._towers_in_range) > 0) and self.isAlive() and self.isShooting():
            #create the projectile and register it as an observer of a tower
            target_tower_id = random.randint(0, (len(self._towers_in_range)-1))
            self._towers_in_range[target_tower_id].registerObserver(self._projectile(
                self._canvas, self.getCenter(), self._towers_in_range[target_tower_id]))
            self._canvas.after(self._shoot_delay, self.shoot)

    '''Subject-Related Functions'''
    def registerObserver(self, observer): self._observers.append(observer)
    def removeObserver(self, observer): self._observers.remove(observer)
    def removeAllObservers(self): self._observers = []
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
        if isinstance(changed_thing, AbstractTower):
            self.processChangedTower(changed_thing)
        else: raise TypeError
    def processChangedTower(self, changed_tower):
        if not changed_tower.isAlive():
            if changed_tower in self._towers_in_range:
                self._towers_in_range.remove(changed_tower)
            if self._projectile != None: self.stopShooting()


#########################################
#         ABSTRACT INVADER CAR          #
#########################################
class AbstractInvaderCar(AbstractInvader):
    def __init__(self, canvas, path):
        AbstractInvader.__init__(self, canvas, path)
        self._passengers = []
        self._num_passengers = None
        self._spawn_rate = None #IN MILLISECONDS
        self._delete_delay = None #IN MILLISECONDS
        self._passengers_released = False
        self._dead_shape = None
        self._wave_manager = getWaveManager()

    # Overriding the abstract invader's take damage method to spawn invaders when dead.
    def takeDamage(self, damage):
        self._health -= damage
        self._health_bar.subtractHealth(damage)
        if self._health <= 0:
            self._alive = False
            self._homebase.addGold(self._gold_prize)
            self._shape.__delete__()
            self._shape = ImageRendering(self._canvas, self.getCenter(), self._dead_image)
            self._shape.render()
            self.releasePassengers()

    def setPassengers(self, passengers):
        self._passengers = passengers
        self._num_passengers = len(self._passengers)
    def setSpawnRate(self, rate):
        self._spawn_rate = rate
        self._delete_delay = rate
    def releasePassengers(self):
        if (len(self._passengers) > 0):
            released_passenger = self._passengers[0](self._canvas, self._path)
            released_passenger.registerObserver(self._wave_manager)
            self._wave_manager.addActiveInvader(released_passenger)
            self._passengers.remove(self._passengers[0])
            self._canvas.after(self._spawn_rate, self.releasePassengers)
        else:
            self._passengers_released = True
            self.setChanged()
            self.removeAllObservers()
            self.__delete__()

    def quickDelete(self):
        self._alive = False
        self._moveBehavior._isMoving = False
        self._towers_in_range = []
        self._shooting = False
        self._shape.__delete__()
        self._burn_shape.__delete__()
        self._health_bar.__delete__()
        del self

    def __delete__(self):
        self._shape.__delete__()
        self._health_bar.__delete__()
        del self


##########################################
#           INVADER THAT MOVES           #
##########################################
class InvaderThatMoves(AbstractInvader):
    def __init__(self, canvas, path):
        AbstractInvader.__init__(self, canvas, path)
        self._health = 50
        self._damage = 10
        self._gold_prize = 5
        self._speed = 1
        self._size = 4
        self._color = 'yellow'
        self._range_factor = 1
        self._moveBehavior = CellsInPath(self._path, self._speed)
        self._shape = StickManRendering(self._canvas, self._moveBehavior.getCenter(), self._size, self._color)
        self._burn_shape = BurnRendering(self._canvas, self._moveBehavior.getCenter())
        self._health_bar = HealthBarRendering(self._canvas, self._health,
                            self._shape.getBottomLeftCorner(), self._shape.getRightmostPoint())
        self.render()

##########################################
#            NYAN CAT INVADER            #
##########################################
class NyanCatInvader(AbstractInvader):
    def __init__(self, canvas, path):
        AbstractInvader.__init__(self, canvas, path)
        self._health = 75
        self._damage = 15
        self._gold_prize = 7
        self._speed = 2
        self._range_factor = 3
        self._image = PhotoImage(file="images/tinyRainbowNyanCat-R.gif")
        self._moveBehavior = CellsInPath(self._path, self._speed)
        self._shape = ImageRendering(self._canvas, self._moveBehavior.getCenter(), self._image)
        self._burn_shape = BurnRendering(self._canvas, self._moveBehavior.getCenter())
        self._health_bar = HealthBarRendering(self._canvas, self._health,
                            self._shape.getBottomLeftCorner(), self._shape.getRightmostPoint())
        self.render()

##########################################
#     DUMB TO TARGET POSITION INVADER    #
##########################################
class DumbToTargetPositionInvader(AbstractInvader):
    def __init__(self, canvas, path):
        AbstractInvader.__init__(self, canvas, path)
        self._health = 20
        self._damage = 0
        self._gold_prize = 0
        self._target_position = (300, 500)
        self._starting_cell = self._path.get_cell(0)
        self._size = 8
        self._speed = 1.5
        self._color = 'light blue'
        self._range_factor = 2
        self._shape = CircleRendering(self._canvas, self._starting_cell.getCenter(),
                                        self._size, self._color)
        self._burn_shape = BurnRendering(self._canvas, self._moveBehavior.getCenter())
        self._health_bar = HealthBarRendering(self._canvas, self._health,
                            self._shape.getBottomLeftCorner(), self._shape.getRightmostPoint())
        self._moveBehavior = TowardsTargetPosition(self._speed, self._starting_cell.getCenter(), self._target_position,)
        self.render()

##########################################
#       SHOOTING NYAN CAT INVADER        #
##########################################
class ShootingNyanCatInvader(AbstractInvader):
    def __init__(self, canvas, path):
        AbstractInvader.__init__(self, canvas, path)
        self._health = 100
        self._damage = 15
        self._gold_prize = 10
        self._start_position = path.get_cell(0).getCenter()
        self._speed = .85
        self._range_factor = 3
        self._moveBehavior = CellsInPath(self._path, self._speed)
        self._coordsInRange = self.getCoordsInRange(self._range_factor)
        self._image = PhotoImage(file="images/tinyRainbowNyanCat-L.gif")
        self._shape = ImageRendering(self._canvas, self._start_position, self._image)
        self._burn_shape = BurnRendering(self._canvas, self._moveBehavior.getCenter())
        self._health_bar = HealthBarRendering(self._canvas, self._health,
                            self._shape.getBottomLeftCorner(), self._shape.getRightmostPoint())
        self._path = path
        self._shoot_delay = 750
        self._can_shoot = True
        self._projectile = HomingArrow
        self.render()


##########################################
#            STICK MAN ARCHER            #
##########################################
class StickManArcher(AbstractInvader):
    def __init__(self, canvas, path):
        AbstractInvader.__init__(self, canvas, path)
        self._health = 125
        self._damage = 10
        self._speed = 1
        self._size = 6
        self._gold_prize = 12
        self._color = '#666666'
        self._range_factor = 2
        self._moveBehavior = CellsInPath(self._path, self._speed)
        self._shape = StickManRendering(self._canvas, self.getCenter(), self._size, self._color)
        self._burn_shape = BurnRendering(self._canvas, self._moveBehavior.getCenter())
        self._health_bar = HealthBarRendering(self._canvas, self._health,
                            self._shape.getBottomLeftCorner(), self._shape.getRightmostPoint())
        self._coordsInRange = self.getCoordsInRange(self._range_factor)
        self._shoot_delay = 600
        self._can_shoot = True
        self._projectile = HomingArrow
        self.render()

#########################################
#            KILLER RABBIT              #
#########################################
class KillerRabbit(AbstractInvader):
    def __init__(self, canvas, path):
        AbstractInvaderCar.__init__(self, canvas, path)
        self._health = 50
        self._damage = 20
        self._gold_prize = 3
        self._speed = 1.75
        self._moveBehavior = CellsInPath(self._path, self._speed)
        self._image = PhotoImage(file="images/MP-killerRabbit-15px.gif")
        self._shape = ImageRendering(self._canvas, self.getCenter(), self._image)
        self._burn_shape = BurnRendering(self._canvas, self._moveBehavior.getCenter())
        self._health_bar = HealthBarRendering(self._canvas, self._health,
                            self._shape.getBottomLeftCorner(), self._shape.getRightmostPoint())
        self.render()

#########################################
#               PYROMANCER              #
#########################################
class Pyromancer(AbstractInvader):
    def __init__(self, canvas, path):
        AbstractInvaderCar.__init__(self, canvas, path)
        self._health = 150
        self._damage = 10
        self._gold_prize = 12
        self._speed = 1
        self._size = 6
        self._color = '#ad0000'
        self._range_factor = 2
        self._moveBehavior = CellsInPath(self._path, self._speed)
        self._shape = StickManRendering(self._canvas, self.getCenter(), self._size, self._color)
        self._burn_shape = BurnRendering(self._canvas, self.getCenter())
        self._health_bar = HealthBarRendering(self._canvas, self._health,
                                    self._shape.getBottomLeftCorner(), self._shape.getRightmostPoint())
        self._coordsInRange = self.getCoordsInRange(self._range_factor)
        self._shoot_delay = 500
        self._can_shoot = True
        self._projectile = HomingFireball
        self.render()

#########################################
#          NYAN INVADER CAR             #
#########################################
class NyanInvaderCar(AbstractInvaderCar):
    def __init__(self, canvas, path):
        AbstractInvaderCar.__init__(self, canvas, path)
        self._health = 250
        self._damage = 100
        self._gold_prize = 17
        self._speed = 1
        self.setPassengers([NyanCatInvader, NyanCatInvader, NyanCatInvader, NyanCatInvader, NyanCatInvader])
        self.setSpawnRate(750)
        self._image = PhotoImage(file="images/InvaderCar-transparent.gif")
        self._dead_image = PhotoImage(file="images/explosion.gif")
        self._moveBehavior = CellsInFuturePath(self._path, self._speed)
        self._shape = ImageRendering(self._canvas, self.getCenter(), self._image)
        self._burn_shape = BurnRendering(self._canvas, self._moveBehavior.getCenter())
        self._health_bar = HealthBarRendering(self._canvas, self._health,
                            self._shape.getBottomLeftCorner(), self._shape.getRightmostPoint())
        self.render()


#########################################
#            TROJAN RABBIT              #
#########################################
class TrojanRabbit(AbstractInvaderCar):
    def __init__(self, canvas, path):
        AbstractInvaderCar.__init__(self, canvas, path)
        self._health = 400
        self._damage = 200
        self._gold_prize = 27
        self._speed = .7
        self.setPassengers([KillerRabbit, KillerRabbit, KillerRabbit, KillerRabbit, KillerRabbit,
                            KillerRabbit, KillerRabbit, KillerRabbit, KillerRabbit, KillerRabbit])
        self.setSpawnRate(400)
        self._image = PhotoImage(file="images/MP-TrojanRabbit-30px.gif")
        self._dead_image = PhotoImage(file="images/MP-TrojanRabbit-30px-Dead.gif")
        self._moveBehavior = CellsInFuturePath(self._path, self._speed)
        self._shape = ImageRendering(self._canvas, self.getCenter(), self._image)
        self._burn_shape = BurnRendering(self._canvas, self._moveBehavior.getCenter())
        self._health_bar = HealthBarRendering(self._canvas, self._health,
                            self._shape.getBottomLeftCorner(), self._shape.getRightmostPoint())
        self.render()

#########################################
#       PYROMANCER INVADER CAR          #
#########################################
class PyromancerInvaderCar(AbstractInvaderCar):
    def __init__(self, canvas, path):
        AbstractInvaderCar.__init__(self, canvas, path)
        self._health = 250
        self._damage = 100
        self._gold_prize = 17
        self._speed = 1
        self.setPassengers([Pyromancer, Pyromancer, Pyromancer, Pyromancer, Pyromancer])
        self.setSpawnRate(750)
        self._image = PhotoImage(file="images/InvaderCar-transparent.gif")
        self._dead_image = PhotoImage(file="images/explosion.gif")
        self._moveBehavior = CellsInFuturePath(self._path, self._speed)
        self._shape = ImageRendering(self._canvas, self.getCenter(), self._image)
        self._burn_shape = BurnRendering(self._canvas, self._moveBehavior.getCenter())
        self._health_bar = HealthBarRendering(self._canvas, self._health,
                            self._shape.getBottomLeftCorner(), self._shape.getRightmostPoint())
        self.render()

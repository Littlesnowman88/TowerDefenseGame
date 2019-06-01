from InvaderClasses import *
from WaveManager import *
from Subject_Observer import Subject, Observer
from InvaderAbstractFactory import *
from PathManager import *
import random

class AbstractWave(implements(Subject), implements(Observer)):
    def __init__(self, canvas, offset):
        self._wave_manager = getWaveManager()
        self._canvas = canvas
        self._invader_order = []
        self._invader_list = []
        self._offset = offset #IN MILLISECONDS
        self._observers_list = []
        self._changed = False
        self._current_invader = None
        self._invader_factory = getInvaderAbstractFactory()
        self._path_manager = getPathManager()
    def setOffset(self, offset): self._offset = offset
    def isDepleted(self):
        if len(self._invader_list) == 0:
            return True
        return False
    def getInvaderOrder(self):
        return self._invader_order
    def getInvaders(self):
        return self._invader_list
    def addInvader(self, invader):
        self._invader_list.append(invader)
    def removeInvader(self, invader):
        self._invader_list.remove(invader)
    def deployInvaders(self):
        if (len(self._invader_order) > 0):
            self._current_invader = self._invader_factory.createInvader(self._invader_order.pop(0), self._canvas, self._path_manager.getRandomPath())
            self._invader_list.append(self._current_invader)
            self._wave_manager.addActiveInvader(self._current_invader)
            self._current_invader.registerObserver(self)
            self._current_invader.registerObserver(self._wave_manager)
            self._canvas.after(self._offset, self.deployInvaders)

    def __delete__(self):
        self._invader_order = []
        self._invader_list = []
        self.removeAllObservers()
        del self

    '''Wave as a Subject of the Wave Manager'''
    def registerObserver(self, observer):
        self._observers_list.append(observer)
    def removeObserver(self, observer):
        self._observers_list.remove(observer)
    def removeAllObservers(self):
        self._observers_list = []
    def isChanged(self):
        return self._changed
    def setChanged(self):
        self._changed = True
        self.notifyObservers()
    def notifyObservers(self):
        for observer in self._observers_list:
            observer.update(self)
        self._changed = False

    '''Wave as an observer of its invaders'''
    def update(self, changed_thing):
        if isinstance(changed_thing, AbstractInvader):
            self.processInvader(changed_thing)
        else:
            raise TypeError
    def processInvader(self, invader):
        if not invader.isAlive():
            try: self.removeInvader(invader)
            except ValueError: pass
            if self.isDepleted():
                self.setChanged()


class SampleWave(AbstractWave):
    def __init__(self, canvas, offset):
        AbstractWave.__init__(self, canvas, offset)
        self._invader_order = [InvaderThatMoves, InvaderThatMoves, NyanCatInvader, NyanCatInvader, ShootingNyanCatInvader, StickManArcher,
                           InvaderThatMoves, InvaderThatMoves,NyanInvaderCar, StickManArcher, ShootingNyanCatInvader, NyanCatInvader, StickManArcher,
                           NyanCatInvader, NyanInvaderCar, TrojanRabbit, StickManArcher, StickManArcher]
class RandomWave(AbstractWave):
    def __init__(self, canvas, offset, num_invaders=10):
        AbstractWave.__init__(self, canvas, offset)
        self._possible_invaders = self._invader_factory.getTypesOfInvaders()
        for invader in range(num_invaders):
            self._invader_order.append(self._possible_invaders[random.randint(0, (len(self._possible_invaders) - 1))])

class WaveFromFile(AbstractWave):
    def __init__(self, canvas, offset):
        AbstractWave.__init__(self, canvas, offset)
    def addInvader(self, invader): self._invader_order.append(invader)


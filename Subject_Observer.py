from interface import Interface

class Subject(Interface):
    def registerObserver(self, observer):
        raise NotImplementedError
    def removeObserver(self, observer):
        raise NotImplementedError
    def removeAllObservers(self):
        raise NotImplementedError
    def isChanged(self):
        raise NotImplementedError
    def setChanged(self):
        raise NotImplementedError
    def notifyObservers(self):
        raise NotImplementedError

class Observer(Interface):
    def update(self, changed_thing):
        raise NotImplementedError
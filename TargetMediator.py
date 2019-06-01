__target_mediator = None
def getTargetMediator():
    from interface import implements
    from TowerClasses import AbstractTower
    from InvaderClasses import AbstractInvader
    from Subject_Observer import Observer

    class TargetMediator(implements(Observer)):
        def __init__(self):
            self._tower_list = []
            self._invader_list = []
            self._projectile_list = []

        def getTowers(self):
            return self._tower_list
        def addTower(self, tower):
            self._tower_list.append(tower)
            #then, add invaders to the tower's possitle targets and notify invaders of the tower's existence
            for invader in self._invader_list:
                tower.addActiveInvader(invader)
                tower.registerObserver(invader)
                invader.addActiveTower(tower)
                invader.registerObserver(tower)
        def removeTower(self, tower):
            self._tower_list.remove(tower)
            #then notify invaders that you did so
            for invader in self._invader_list:
                invader.removeActiveTower(tower)

        def setInvaders(self, list_of_invaders):
            self._invader_list = list_of_invaders
        def getInvaders(self):
            return self._invader_list
        def addInvader(self, invader):
            self._invader_list.append(invader)
            for tower in self._tower_list:
                invader.addActiveTower(tower)
                invader.registerObserver(tower)
                tower.addActiveInvader(invader)
                tower.registerObserver(invader)
        def removeInvader(self, invader):
            self._invader_list.remove(invader)
            for tower in self._tower_list:
                tower.removeActiveInvader(invader)
        def addProjectile(self, projectile): self._projectile_list.append(projectile)
        def removeProjectile(self, projectile): self._projectile_list.remove(projectile)

        def update(self, changed_thing):
            if isinstance(changed_thing, AbstractTower):
                self.processTower(changed_thing)
            elif isinstance(changed_thing, AbstractInvader):
                self.processInvader(changed_thing)
            else:
                raise TypeError()

        def processTower(self, tower):
            if not tower.isAlive(): self.removeTower(tower)
        def processInvader(self, invader):
            if not invader.isAlive(): self.removeInvader(invader)

        def __delete__(self):
            for tower in self._tower_list:
                tower.quickDelete()
            for invader in self._invader_list:
                invader.quickDelete()
            for projectile in self._projectile_list:
                projectile.__delete__()
            del self

    global __target_mediator
    if __target_mediator == None:
        __target_mediator = TargetMediator()
    return __target_mediator

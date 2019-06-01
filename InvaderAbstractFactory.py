from InvaderClasses import *
from PathManager import *
__invader_abstract_factory = None
def getInvaderAbstractFactory():
    class InvaderAbstractFactory:
        def __init__(self):
            self._path_manager = getPathManager()

        def createInvader(self, invader_class, canvas, path):
            if (invader_class == InvaderThatMoves) or (invader_class == "InvaderThatMoves"):
                return InvaderThatMoves(canvas, path)
            elif (invader_class == NyanCatInvader) or (invader_class == "NyanCatInvader"):
                return NyanCatInvader(canvas, path)
            elif (invader_class == StickManArcher) or (invader_class == "StickManArcher"):
                return StickManArcher(canvas, path)
            elif (invader_class == ShootingNyanCatInvader) or (invader_class == "ShootingNyanCatInvader"):
                return ShootingNyanCatInvader(canvas, path)
            elif (invader_class == Pyromancer) or (invader_class == "Pyromancer"):
                return Pyromancer(canvas, path)
            elif (invader_class == KillerRabbit) or (invader_class == "KillerRabbit"):
                return KillerRabbit(canvas, path)
            elif (invader_class == NyanInvaderCar) or (invader_class == "NyanInvaderCar"):
                return NyanInvaderCar(canvas, self._path_manager.getPathCopy(path))
            elif (invader_class == PyromancerInvaderCar) or (invader_class == "PyromancerInvaderCar"):
                return PyromancerInvaderCar(canvas, self._path_manager.getPathCopy(path))
            elif (invader_class == TrojanRabbit) or (invader_class == "TrojanRabbit"):
                return TrojanRabbit(canvas, self._path_manager.getPathCopy(path))
            else: raise TypeError("Here is the invader class you printed: {0}", invader_class)

        def getTypesOfInvaders(self):
            return [InvaderThatMoves, NyanCatInvader, StickManArcher, ShootingNyanCatInvader,
                    KillerRabbit, Pyromancer, NyanInvaderCar, PyromancerInvaderCar, TrojanRabbit]

    global __invader_abstract_factory
    if __invader_abstract_factory == None:
        __invader_abstract_factory = InvaderAbstractFactory()
    return __invader_abstract_factory
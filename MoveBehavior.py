from interface import Interface, implements
import math

class MoveBehavior(Interface):
    def getCenter(self):
        raise NotImplementedError
    def isMoving(self):
        return NotImplementedError
    def _compute_new_position(self):
        raise NotImplementedError
    def move(self):
        raise NotImplementedError

class AbstractMovement():
    def __init__(self, speed):
        self._speed = speed
        self._isMoving = True
        self._hasMoved = False
        self._distance_tracker = 0
        self._xposition = None
        self._yposition = None
        self._target_position = None
        self._target_reached = False

    def getCenter(self):
        return (self._x, self._y)
    def isMoving(self):
        return self._isMoving
    def stopMoving(self): self._isMoving = False
    def getHasMoved(self):
        return self._hasMoved
    def clearHasMoved(self):
        self._hasMoved = False
    def checkIfAtTarget(self):
        # if it's really close to its target
        if  (   ((-1*self._speed) <= (self._target_x - self._x))
            and (( 1*self._speed) >= (self._target_x - self._x))
            and ((-1*self._speed) <= (self._target_y - self._y))
            and (( 1*self._speed) >= (self._target_y - self._y))):
            self._target_reached = True
            self._isMoving = False
        else:
            self._target_reached = False
    def isAtTarget(self):
        return self._target_reached
    def updateHasMoved(self, distance):
        #self._distance_tracker += distance
        if ((-2 * self._speed) <= self._distance_tracker <= (2*self._speed)):
            #if an object moves two times. These numbers could be stored in a variable, I suppose, and the variable could be passed in.
            self._distance_tracker = 0
            self._hasMoved = True


class CellsInPath(AbstractMovement, implements(MoveBehavior)):
    def __init__(self, path, speed):
        AbstractMovement.__init__(self, speed)
        self._path = path
        self._destination_cell_id = 0
        self._destination_cell = self._path.get_cell(0)
        self._x , self._y = self._destination_cell.getCenter()
        self._target_position = self._path.get_cell(len(self._path) -1).getCenter() #center of final cell in path #THIS DID NOT WORK FOR LYDIA
        self._target_x, self._target_y = self._target_position

    def _compute_new_position(self):
        self._compute_x_position()
        self._compute_y_position()
    def _find_next_cell(self):
        try:
            self._destination_cell_id += 1
            self._destination_cell = self._path.get_cell(self._destination_cell_id)
        except IndexError:
            self._isMoving = False
            self.checkIfAtTarget()

    def _compute_x_position(self):
        d = self._destination_cell.get_center_x() - self._x
        if d >= self._speed:
            self._xposition = self._speed
        elif ((-1*self._speed) < d) and (self._speed > d):
            self._xposition = 0
        else:
            self._xposition = -1 * self._speed
    def _compute_y_position(self):
        d = self._destination_cell.get_center_y() - self._y
        if d >= self._speed:
            self._yposition = self._speed
        elif ((-1*self._speed) < d) and (self._speed > d):
            self._yposition = 0
        else:
            self._yposition = -1 * self._speed
    def move(self):
        if (self._xposition == 0) and (self._yposition == 0):
            self._find_next_cell()
        self._compute_new_position()
        self._x += self._xposition #move X
        self._y += self._yposition #move Y
        self.updateHasMoved(self._xposition + self._yposition)

class CellsInFuturePath(CellsInPath):
    def __init__(self, path, speed):
        CellsInPath.__init__(self, path, speed)
        self._current_cell = self._path.get_cell(0)

    def _get_current_cell(self): return self._current_cell
    def _find_next_cell(self):
        try:
            self._current_cell = self._destination_cell
            self._destination_cell = self._path.get_cell(1)
            self._path.remove_cell(self._current_cell)
        except IndexError:
            self._isMoving = False
            self.checkIfAtTarget()


class TowardsTargetObject(AbstractMovement, implements(MoveBehavior)):
    def __init__(self, speed, target_object, position):
        AbstractMovement.__init__(self, speed)
        self._target = target_object
        self._position = position
        self._x, self._y = self._position
        self._target_position = self._target.getCenter()
        self._target_x, self._target_y = self._target_position

    def set_target_position(self, position):
        self._target_position = position
        self._target_x, self._target_y = position

    '''THIS OVERWRITES the abstract movement's method to also make sure that its target object still exists'''
    def checkIfAtTarget(self):
        # if it's really close to its target
        if  (   ((-1*self._speed) <= (self._target_x - self._x))
            and (( 1*self._speed) >= (self._target_x - self._x))
            and ((-1*self._speed) <= (self._target_y - self._y))
            and (( 1*self._speed) >= (self._target_y - self._y))):
            if (self._target.isAlive()) and (self._target != None):
                self._target_reached = True
                self._isMoving = False
        else:
            self._target_reached = False

    def _compute_new_position(self):
        self._compute_x_position()
        self._compute_y_position()
    def _compute_x_position(self):
        d = self._target_x - self._x
        if d >= self._speed:
            self._xposition = self._speed
        elif ((-1*self._speed) < d) and (self._speed > d):
            self._xposition = 0
        else:
            self._xposition = -1 * self._speed
    def _compute_y_position(self):
        d = self._target_y - self._y
        if d >= self._speed:
            self._yposition = self._speed
        elif ((-1*self._speed) < d) and (self._speed > d):
            self._yposition = 0
        else:
            self._yposition = -1 * self._speed

    def move(self):
        self.checkIfAtTarget()
        if not self.isAtTarget():
            self._compute_new_position()
            if self.isMoving():
                self._x += self._xposition #move X
                self._y += self._yposition #move Y
                self.updateHasMoved(self._xposition + self._yposition)


class TowardsTargetPosition(AbstractMovement, implements(MoveBehavior)):
    def __init__(self, speed, position, target_position):
        AbstractMovement.__init__(self, speed)
        self._x, self._y = position
        self._target_position = target_position
        self._target_x, self._target_y = self._target_position

    def _compute_new_position(self):
        self._compute_x_position()
        self._compute_y_position()
    def _compute_x_position(self):
        d = self._target_x - self._x
        if d >= self._speed:
            self._xposition = self._speed
        elif ((-1*self._speed) < d) and (self._speed > d):
            self._xposition = 0
        else:
            self._xposition = -1 * self._speed
    def _compute_y_position(self):
        d = self._target_y - self._y
        if d >= self._speed:
            self._yposition = self._speed
        elif ((-1*self._speed) < d) and (self._speed > d):
            self._yposition = 0
        else:
            self._yposition = -1 * self._speed
    def move(self):
        if (self._x, self._y) != self._target_position:
            self._compute_new_position()
        if (self._xposition != 0) or (self._yposition != 0):
            self._x += self._xposition #move X
            self._y += self._yposition #move Y
            self.updateHasMoved(self._xposition + self._yposition)
        else:
            self._isMoving = False
            self.checkIfAtTarget()


class UpForDistance(AbstractMovement, implements(MoveBehavior)):
    def __init__(self, distance, speed, position):
        AbstractMovement.__init__(self, speed)
        self._distance = distance
        self._x , self._y = position
        self._target_y = self._y - self._distance
        self._target_position = (self._x, self._target_y)

    def _compute_new_position(self):
        self._compute_y_position()
    def _compute_y_position(self, speed):
        if (self._target - self._y) >= 0:
            #if an object is above or on its target for some reason, stop it's movement
            self._yposition = 0
            self._isMoving = False
            self.checkIfAtTarget()
        else:
            self._yposition = -1 * self._speed
    def move(self):
        self._compute_new_position()
        self._y += self._yposition #move Y
        self.updateHasMoved(self._yposition)


class UpRightForDistance(AbstractMovement, implements(MoveBehavior)):
    def __init__(self, distance, speed, position):
        AbstractMovement.__init__(self, speed)
        self._distance = distance
        self._x , self._y = position
        self._target_x = self._x + self._distance
        self._target_y = self._y - self._distance
        self._target_position = (self._target_x, self._target_y)

    def _compute_new_position(self):
        self._compute_x_position()
        self._compute_y_position()
    def _compute_x_position(self):
        if (self._target_x - self._x) <= 0:
            #if an object is right of or on its target, stop it's movement
            self._xposition = 0
        else:
            self._xposition = 1 * self._speed
    def _compute_y_position(self):
        if (self._target_y - self._y) >= 0:
            #if an object is above or on its target, stop it's movement
            self._yposition = 0
        else:
            self._yposition = -1 * self._speed
    def move(self):
        if (self._x, self._y) != (self._target_x, self._target_y):
            self._compute_new_position()
        if (self._xposition != 0) or (self._yposition != 0):
            self._x += self._xposition #move X
            self._y += self._yposition #move Y
            self.updateHasMoved(self._xposition + self._yposition)
        else:
            self._isMoving = False
            self.checkIfAtTarget()


class RightForDistance(AbstractMovement, implements(MoveBehavior)):
    def __init__(self, distance, speed, position):
        AbstractMovement.__init__(self, speed)
        self._distance = distance
        self._x , self._y = position
        self._target_x = self._x + self._distance
        self._target_position = (self._target_x, self._y)

    def _compute_new_position(self):
        self._compute_x_position()
    def _compute_x_position(self):
        if (self._target - self._x) <= 0:
            #if an object is right of or on its target, stop it's movement
            self._xposition = 0
            self._isMoving = False
            self.checkIfAtTarget()
        else:
            self._xposition = 1 * self._speed
    def move(self):
        self._compute_new_position()
        self._x += self._xposition #move X
        self.updateHasMoved(self._xposition)


class DownRightForDistance(AbstractMovement, implements(MoveBehavior)):
    def __init__(self, distance, speed, position):
        AbstractMovement.__init__(self, speed)
        self._distance = distance
        self._x , self._y = position
        self._target_x = self._x + self._distance
        self._target_y = self._y + self._distance
        self._target_position = (self._target_x, self._target_y)

    def _compute_new_position(self):
        self._compute_x_position()
        self._compute_y_position()
    def _compute_x_position(self):
        if (self._target_x - self._x) <= 0:
            #if an object is right of or on its target, stop it's movement
            self._xposition = 0
        else:
            self._xposition = 1 * self._speed
    def _compute_y_position(self):
        if (self._target_y - self._y) <= 0:
            #if an object is above or on its target, stop it's movement
            self._yposition = 0
        else:
            self._yposition = 1 * self._speed
    def move(self):
        if (self._x, self._y) != (self._target_x, self._target_y):
            self._compute_new_position()
        if (self._xposition != 0) or (self._yposition != 0):
            self._x += self._xposition #move X
            self._y += self._yposition #move Y
            self.updateHasMoved(self._xposition + self._yposition)
        else:
            self._isMoving = False
            self.checkIfAtTarget()


class DownForDistance(AbstractMovement, implements(MoveBehavior)):
    def __init__(self, distance, speed, position):
        AbstractMovement.__init__(self, speed)
        self._distance = distance
        self._x , self._y = position
        self._target_y = self._y + self._distance
        self._target_position = (self._x, self._target_y)

    def _compute_new_position(self):
        self._compute_y_position()
    def _compute_y_position(self):
        if (self._target - self._y) <= 0:
            #if an object is below or on its target for some reason, stop it's movement
            self._yposition = 0
            self._isMoving = False
            self.checkIfAtTarget()
        else:
            self._yposition = 1 * self._speed
    def move(self):
        self._compute_new_position()
        self._y += self._yposition #move Y
        self.updateHasMoved(self._yposition)


class DownLeftForDistance(AbstractMovement, implements(MoveBehavior)):
    def __init__(self, distance, speed, position):
        AbstractMovement.__init__(self, speed)
        self._distance = distance
        self._x , self._y = position
        self._target_x = self._x - self._distance
        self._target_y = self._y + self._distance
        self._target_position = (self._target_x, self._target_y)

    def _compute_new_position(self):
        self._compute_x_position()
        self._compute_y_position()
    def _compute_x_position(self):
        if (self._target_x - self._x) >= 0:
            #if an object is right of or on its target, stop it's movement
            self._xposition = 0
        else:
            self._xposition = -1 * self._speed
    def _compute_y_position(self):
        if (self._target_y - self._y) <= 0:
            #if an object is above or on its target, stop it's movement
            self._yposition = 0
        else:
            self._yposition = 1 * self._speed
    def move(self):
        if (self._x, self._y) != (self._target_x, self._target_y):
            self._compute_new_position()
        if (self._xposition != 0) or (self._yposition != 0):
            self._x += self._xposition #move X
            self._y += self._yposition #move Y
            self.updateHasMoved(self._xposition + self._yposition)
        else:
            self._isMoving = False
            self.checkIfAtTarget()


class LeftForDistance(AbstractMovement, implements(MoveBehavior)):
    def __init__(self, distance, speed, position):
        AbstractMovement.__init__(self, speed)
        self._distance = distance
        self._x , self._y = position
        self._target_x = self._x - self._distance
        self._target_position = (self._target_x, self._y)

    def _compute_new_position(self):
        self._compute_x_position()
    def _compute_x_position(self):
        if (self._target - self._x) >= 0:
            #if an object is left of or on its target, stop it's movement
            self._xposition = 0
            self._isMoving = False
            self.checkIfAtTarget()
        else:
            self._xposition = -1 * self._speed
    def move(self):
        self._compute_new_position()
        self._x += self._xposition #move X
        self.updateHasMoved(self._xposition)

class UpLeftForDistance(AbstractMovement, implements(MoveBehavior)):
    def __init__(self, distance, speed, position):
        AbstractMovement.__init__(self, speed)
        self._distance = distance
        self._x , self._y = position
        self._target_x = self._x - self._distance
        self._target_y = self._y - self._distance
        self._target_position = (self._target_x, self._target_y)

    def _compute_new_position(self):
        self._compute_x_position()
        self._compute_y_position()
    def _compute_x_position(self):
        if (self._target_x - self._x) >= 0:
            #if an object is right of or on its target, stop it's movement
            self._xposition = 0
        else:
            self._xposition = -1 * self._speed
    def _compute_y_position(self):
        if (self._target_y - self._y) >= 0:
            #if an object is above or on its target, stop it's movement
            self._yposition = 0
        else:
            self._yposition = -1 * self._speed
    def move(self):
        if (self._x, self._y) != (self._target_x, self._target_y):
            self._compute_new_position()
        if (self._xposition != 0) or (self._yposition != 0):
            self._x += self._xposition #move X
            self._y += self._yposition #move Y
            self.updateHasMoved(self._xposition + self._yposition)
        else:
            self._isMoving = False
            self.checkIfAtTarget()
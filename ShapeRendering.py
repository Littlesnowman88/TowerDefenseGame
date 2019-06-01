from interface import Interface, implements
import types

class ShapeRendering(Interface):
    def getBottomLeftCorner(self):
        raise NotImplementedError
    def getRightmostPoint(self):
        raise NotImplementedError
    def setSize(self, size):
        raise NotImplementedError
    def setColor(self, color):
        raise NotImplementedError()
    def assignShapeXY(self, position):
        raise NotImplementedError
    def render(self):
        raise NotImplementedError()

class AbstractShape(implements(ShapeRendering)):
    def __init__(self, canvas, position):
        self._canvas = canvas
        self._position = position
        self._x, self._y = position
    def getBottomLeftCorner(self): raise RuntimeError
    def getRightmostPoint(self): raise RuntimeError
    def setSize(self, size): raise RuntimeError
    def setColor(self, color): raise RuntimeError
    def assignShapeXY(self, position): raise RuntimeError
    def render(self): raise RuntimeError
    def __delete__(self):
        if not isinstance(self._id, list):
            self._canvas.delete(self._id)
        else:
            for id in self._id:
                self._canvas.delete(id)


class HealthBarRendering(AbstractShape):
    def __init__(self, canvas, max_health, top_left_position, right_x):
        self._canvas = canvas
        self._max_health = max_health
        self._left_x, self._top_y = top_left_position
        self._initial_right_x = right_x
        self._initial_width = self._initial_right_x - self._left_x
        self._top_y += 2
        self._bottom_y = self._top_y + 4
        self._health = self._max_health
        self._right_x = right_x
        self._color = "#00ad00"
        self._id = None

    def setColor(self, color): self._color = color
    def subtractHealth(self, damage):
        self._health -= damage
        self.assignShapeXY((self._left_x, self._top_y -2))
        self.render()
    def assignShapeXY(self, position):
        self._left_x, self._top_y = position
        self._top_y += 2
        self._bottom_y = self._top_y + 4
        self._right_x = self._left_x + ((self._initial_width *self._health) / self._max_health)
    def render(self):
        self._canvas.delete(self._id)
        self._id = self._canvas.create_rectangle(self._left_x, self._top_y,
                            self._right_x, self._bottom_y, fill = self._color)
    def __delete__(self):
        self._canvas.delete(self._id)
        del self

class BurnRendering(AbstractShape):
    def __init__(self, canvas, position):
        AbstractShape.__init__(self, canvas, position)
        self._color = 'red'
        self._size = 6
        self.assignShapeXY(self._position)
        self._id = self._canvas.create_rectangle(0,0,0,0)
        self._canvas.delete(self._id)
    def assignShapeXY(self, position):
        self._position = position
        self._x, self._y = position
        self._ulx = self._x - (self._size / 2)
        self._uly = self._y - (self._size / 2)
        self._lrx = self._x + (self._size / 2)
        self._lry = self._y + (self._size / 2)
    def render(self):
        self._canvas.delete(self._id)
        self._id = self._canvas.create_rectangle(self._ulx, self._uly, self._lrx, self._lry, fill=self._color)
    def unrender(self): self._canvas.delete(self._id)


class CircleRendering(AbstractShape):
    def __init__(self, canvas, position, size, color):
        AbstractShape.__init__(self, canvas, position)
        self._size = size
        self._color = color
        self.assignShapeXY(self._position)
        self._id = None
    def getBottomLeftCorner(self): return (self._leftX, self._rightY)
    def getRightmostPoint(self): return self._rightX
    def assignShapeXY(self, position):
        self._x, self._y = position
        self._leftX = self._x - self._size
        self._leftY = self._y - self._size
        self._rightX = self._x + self._size
        self._rightY = self._y + self._size
    def render(self):
        self._canvas.delete(self._id)
        self._id = self._canvas.create_oval(self._leftX, self._leftY,
                            self._rightX, self._rightY, fill=self._color)


class SquareRendering(AbstractShape):
    def __init__(self, canvas, position, size, color):
        AbstractShape.__init__(self, canvas, position)
        self._size = size
        self._color = color
        self.assignShapeXY(self._position)
        self._id = None
    def getBottomLeftCorner(self): return (self._ulx, self._lry)
    def getRightmostPoint(self): return self._lrx
    def assignShapeXY(self, position):
        self._x, self._y = position
        self._ulx = self._x - self._size
        self._lrx = self._x + self._size
        self._uly = self._y - self._size
        self._lry = self._y + self._size
    def render(self):
        self._canvas.delete(self._id)
        self._id = self._canvas.create_rectangle(self._ulx, self._uly, self._lrx, self._lry,
                                                 fill=self._color)

class DiamondRendering(AbstractShape):
    def __init__(self, canvas, position, size, color):
        AbstractShape.__init__(self, canvas, position)
        self._size = size
        self._color = color
        self.assignShapeXY(self._position)
        self._id = None
    def getBottomLeftCorner(self): return (self._leftX, self._bottomY)
    def getRightmostPoint(self): return (self._rightX)
    def assignShapeXY(self, position):
        self._x, self._y = position
        self._topX = self._x
        self._topY = self._y - self._size
        self._leftX = self._x - self._size
        self._leftY = self._y
        self._bottomX = self._x
        self._bottomY = self._y + self._size
        self._rightX = self._x + self._size
        self._rightY = self._y
    def render(self):
        self._canvas.delete(self._id)
        self._id = self._canvas.create_polygon(self._topX, self._topY, self._leftX, self._leftY,
                                               self._bottomX, self._bottomY, self._rightX, self._rightY,
                                               fill=self._color)

class TriangleRendering(AbstractShape):
    def __init__(self, canvas, position, size, color):
        AbstractShape.__init__(self, canvas, position)
        self._size = size
        self._color = color
        self.assignShapeXY(self._position)
        self._id = None

    def getBottomLeftCorner(self): return (self._bottomLeftX, self._bottomLeftY)
    def getRightmostPoint(self): return self._bottomRightX
    def assignShapeXY(self, position):
        self._x, self._y = position
        self._topX = self._x
        self._topY = self._y - self._size
        self._bottomLeftX = self._topX - self._size
        self._bottomLeftY = self._topY + (2 * self._size)
        self._bottomRightX = self._topX + self._size
        self._bottomRightY = self._bottomLeftY
    def render(self):
        self._canvas.delete(self._id)
        self._id = self._canvas.create_polygon(self._topX, self._topY, self._bottomLeftX,
                                               self._bottomLeftY, self._bottomRightX,
                                               self._bottomRightY,  fill=self._color)

class ImageRendering(AbstractShape):
    def __init__(self, canvas, position, image):
        AbstractShape.__init__(self, canvas, position)
        self._image = image
        self.assignShapeXY(self._position)
        self._id = None
    def getBottomLeftCorner(self): return (self._x - 15, self._y + 15) #half a cell left and down
    def getRightmostPoint(self): return (self._x + 15) #half a cell to the right
    def setColor(self, color): raise RuntimeError #uses an image, not a color
    def setSize(self, size): raise RuntimeError #uses an image that (for now?) must be sized correctly before implementing it
    def assignShapeXY(self, position):
        self._x, self._y = position
        pass  #XY taken care of by Invader and the "shape", or image, is implemented in render
    def render(self):
        self._canvas.delete(self._id)
        self._id = self._canvas.create_image(self._x, self._y, image = self._image)

class StickManRendering(AbstractShape):
    def __init__(self, canvas, position, size, color):
        AbstractShape.__init__(self, canvas, position)
        self._size = size
        self._color = color
        self.assignShapeXY(self._position)
        self._id = []
    def getBottomLeftCorner(self): return ((self._x - (self._size/2)), self._y + ((3*self._size)/2))
    def getRightmostPoint(self): return (self._x + (self._size/2))
    def assignShapeXY(self, position):
        self._x, self._y = position
        self.assignHeadXY()
        self.assignBodyXY()
        self.assignLeftArmXY()
        self.assignRightArmXY()
        self.assignLeftLegXY()
        self.assignRightLegXY()
    def assignHeadXY(self):
        self._headULX = self._x - (self._size / 2)
        self._headULY = self._y - ((3 * self._size) / 2)
        self._headLRX = self._x + (self._size / 2)
        self._headLRY = self._y - (self._size / 2)
    def assignBodyXY(self):
        self._bodyX = self._x
        self._bodyTopY = self._y - (self._size / 2)
        self._bodyBottomY = self._y + (self._size / 2)
    def assignLeftArmXY(self):
        '''The stick man's actual left arm, not the arm on your left (instead, it's the arm on your right)'''
        self._left_armURX = self._x + (self._size / 2)
        self._left_armURY = self._y - (self._size / 3)
        self._left_armLLX = self._x
        self._left_armLLY = self._y
    def assignRightArmXY(self):
        '''The stick man's actual right arm, not the arm on your right (instead, it's the arm on your left)'''
        self._right_armULX = self._x - (self._size / 2)
        self._right_armULY = self._y - (self._size / 3)
        self._right_armLRX = self._x
        self._right_armLRY = self._y
    def assignLeftLegXY(self):
        '''The stick man's actual left leg, not the leg on your left (instead, it's the leg on your right)'''
        self._left_legULX = self._x
        self._left_legULY = self._y + (self._size / 2)
        self._left_legLRX = self._x + (self._size / 2)
        self._left_legLRY = self._y + ((3 * self._size) / 2)
    def assignRightLegXY(self):
        '''The stick man's actual right leg, not the leg on your right (instead, it's the leg on your left)'''
        self._right_legURX = self._x
        self._right_legURY = self._y
        self._right_legLLX = self._x - (self._size / 2)
        self._right_legLLY = self._y + ((3 * self._size) / 2)

    def render(self):
        #delete the old stick figure
        for body_part in self._id:
            self._canvas.delete(body_part)
        '''create a stick figure combatant on the screen'''
        self._head = self._canvas.create_oval(self._headULX, self._headULY, self._headLRX, self._headLRY, fill=self._color) # head
        self._body = self._canvas.create_line(self._bodyX, self._bodyTopY, self._bodyX, self._bodyBottomY, fill=self._color) # body
        self._left_arm = self._canvas.create_line(self._left_armURX, self._left_armURY, self._left_armLLX, self._left_armLLY, fill=self._color)  # combatant's left arm
        self._right_arm = self._canvas.create_line(self._right_armLRX, self._right_armLRY, self._right_armULX, self._right_armULY, fill=self._color)  # combatant's right arm
        self._left_leg = self._canvas.create_line(self._left_legULX, self._left_legULY, self._left_legLRX, self._left_legLRY, fill=self._color)  # combatant's left leg
        self._right_leg = self._canvas.create_line(self._right_legURX, self._right_legURY, self._right_legLLX, self._right_legLLY, fill=self._color)  # combatant's right leg
        self._id = [self._head, self._body, self._left_arm, self._right_arm, self._left_leg, self._right_leg]
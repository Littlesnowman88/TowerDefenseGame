from tkinter import *
from PathClass import *
from TargetMediator import *
from WaveManager import *
from PathManager import *
from HomeBase import *
from interface import implements
from Subject_Observer import Observer

TIME_BETWEEN_WAVES = 30    # seconds

class App(implements(Observer)):
    def __init__(self, root):
        self._root = root
        self._gameRunning = False
        self._gameOver = False
        self._currWaveNumber = 0
        self._currWave = None

        self._path_manager = getPathManager()
        self._homebase = getHomeBase()

        self._top_panel = Frame(root)
        self._top_panel.grid(row=0, column=0, rowspan=5, columnspan=12)

        # button frame
        self._button_frame = Frame(self._top_panel).grid(row=0, column=0, columnspan=3)
        self._btStartGame = Button(self._button_frame, activebackground="#0cf700", background="#00c800",
                                   text="Start Game", command=self.startGame)
        self._btStartGame.grid(row=0, column=0, columnspan=2, sticky=W)

        self._btNextWave = Button(self._button_frame, activebackground="#00eaff", background="#00d0ff",
                                  text="Start Wave", command=self.startNextWave)
        self._btNextWave.grid(row=0, column=1, columnspan=3)

        # Next wave text frame
        self._wave_text_frame = Frame(self._top_panel).grid(row=0, column=3, columnspan=5)
        Label(self._wave_text_frame, justify=RIGHT, text="Next wave starts in: ").grid(row=0, column=3, columnspan=4,
                                                                                       sticky=E)
        self._timeLeftTilWave = IntVar()
        self._timeLeftTilWave.set(TIME_BETWEEN_WAVES)
        self._timeLeftLbl = Label(self._wave_text_frame, justify=LEFT, textvariable=self._timeLeftTilWave)
        self._timeLeftLbl.grid(row=0, column=7, sticky=W)

        # Gold frame
        self._gold_frame = Frame(self._top_panel, borderwidth=1, background="#fff0a8").grid(row=1, column=0,
                                                                                            columnspan=2)
        Label(self._gold_frame, justify=RIGHT, text="Gold: ").grid(row=1, column=0, sticky=E)
        self._goldAmtVar = IntVar()
        self._goldAmtVar.set(self._homebase.getGold())
        self._goldLbl = Label(self._gold_frame, justify=LEFT, textvariable=self._goldAmtVar)
        self._goldLbl.grid(row=1, column=1, sticky=W)

        # have to instantiate HomeBase before we can display its health
        self._homebase.registerObserver(self)
        self._homebaseHealthVar = IntVar()
        self._homebaseHealthVar.set(self._homebase.getHealth())

        # Health frame
        self._health_frame = Frame(self._top_panel).grid(row=1, column=3, columnspan=4)
        Label(self._health_frame, text="HomeBase health:").grid(row=1, column=3, columnspan=3, sticky=E)
        self._healthLbl = Label(self._health_frame, textvariable=self._homebaseHealthVar)
        self._healthLbl.grid(row=1, column=6, sticky=W)

        # Costs frame
        self._costs_frame = Frame(self._top_panel, borderwidth=1).grid(row=0, column=9, rowspan=4, columnspan=3)
        Label(self._costs_frame, text="Tower Building Costs:").grid(row=0, column=9, columnspan=3)
        Label(self._costs_frame, text="Blue Circle: 10").grid(row=1, column=9, columnspan=3, sticky=E)
        Label(self._costs_frame, text="Red Square: 35").grid(row=2, column=9, columnspan=3, sticky=E)
        Label(self._costs_frame, text="Green Diamond: 60").grid(row=3, column=9, columnspan=3, sticky=E)

        # Instructions frame
        self._instructions_frame = Frame(self._top_panel).grid(row=2, column=0, rowspan=2, columnspan=8)
        Label(self._instructions_frame,
              text="Press 'b', 'r', & 'g' to set the type of tower that will be built on click.").grid(row=2, column=0,
                                                                                                       columnspan=8)
        Label(self._instructions_frame,
              text="Hold down 'shift' and click to sell a tower and earn back some gold.").grid(row=3, column=0,
                                                                                                columnspan=8)

        # create the canvas
        self._canv = Canvas(root, width=self._path_manager.getCanvasDim(), height=self._path_manager.getCanvasDim())
        self._canv.grid(row=5, column=0, columnspan=12)

        # construct a 2-D grid
        self._grid = []
        for row in range(self._path_manager.getNumCellsPerDim()):
            rowlist = []
            for col in range(self._path_manager.getNumCellsPerDim()):
                cell = Cell(self._canv, col, row, self._path_manager.getCellSize())
                rowlist.append(cell)
            self._grid.append(rowlist)
        self._path_manager.setGrid(self._grid)

        #Initialization of important managers
        self._path_manager.initializeMap()
        self._homebase.setCanvas(self._canv)
        self._homebase.setPosition(self._path_manager.getPathEndCellCoords())
        self._homebase.render()
        self._target_mediator = getTargetMediator()
        self._wave_manager = getWaveManager()
        self._wave_manager.setCanvas(self._canv)
        self._wave_manager.registerObserver(self)
        self._wave_manager.initializeWaves()


    def get_Canvas(self):
        return self._canv

    def startGame(self):
        # TODO: should have Start Wave button disabled and enable it here.
        if not self._gameOver:
            self._gameRunning = True
            # Start the timer, which forces the next wave to start in a few seconds.
            self.updateTimer()

    def startNextWave(self):
        '''Start the next wave now'''
        if not self._gameRunning:
            return
        self._wave_manager.deployWave()
        self._timeLeftTilWave.set(TIME_BETWEEN_WAVES)

    def updateTimer(self):
        timeLeft = self._timeLeftTilWave.get()
        timeLeft -= 1
        self._timeLeftTilWave.set(timeLeft)
        if timeLeft == 0:
            self.startNextWave()
        if self._gameRunning == True:
            self._canv.after(1000, self.updateTimer)

    def update(self, changed_thing):
        if (changed_thing == getWaveManager()):
            self.processWaveManager()

        elif (changed_thing == getHomeBase()):
            self.processHomeBase()

    def processWaveManager(self):
        self._game_over_image = PhotoImage(file="images/MP-Frenchman.gif")
        self._id = self._canv.create_image(300, 300, image=self._game_over_image)
        self._canv.after(5000, self._canv.delete, self._id)
        self._canv.after(5000, self.renderGameOverImage)
        self.stopGame()

    def processHomeBase(self):
        healthLeft = self._homebase.getHealth()
        self._homebaseHealthVar.set(healthLeft)
        goldLeft = self._homebase.getGold()
        self._goldAmtVar.set(goldLeft)
        if not self._homebase.isAlive():
            self.renderGameOverImage()
            self.stopGame()

    def renderGameOverImage(self):
        self._game_over_image = PhotoImage(file="images/gameOver-450px.gif")
        self._id = self._canv.create_image(300, 300, image=self._game_over_image)

    def stopGame(self):
        self._gameRunning = False
        self._gameOver = True
        for row in self._grid:
            for cell in row:
                cell.__delete__()
        self._homebase.__delete__()
        self._wave_manager.__delete__()
        self._target_mediator.__delete__()
        self._canv.after(10000, self.__delete__)

    def __delete__(self):
        self._root.destroy()



root = Tk()
root.title("Calvin Tower Defense")
App(root)
root.wm_attributes('-topmost', 1)
root.mainloop()


if __name__ == '__main__':
    p = Path(4)
    root = Tk()
    root.title("Unittest")
    Application = App(root)
    canvas = Application.get_Canvas()
    cells = [Cell(canvas, 0, 3, 5), Cell(canvas, 1, 3, 5), Cell(canvas, 2, 3, 5),
             Cell(canvas, 3, 3, 5)]
    for c in cells:
        p.add_cell(c)
    assert len(p) == 4

    # Test starting cell not on an edge
    p = Path(4)
    try:
        p.add_cell(Cell(canvas, 2, 2, 5))
        assert False
    except AssertionError:
        pass

    # Test adding diagonally-adjacent cell -- not allowed.
    p = Path(4)
    p.add_cell(Cell(canvas, 3, 3, 5))
    try:
        p.add_cell(Cell(canvas, 2, 2, 5))
        assert False
    except AssertionError:
        pass
    
    # Test adding totally non-adjacent cell -- not allowed.
    p = Path(4)
    p.add_cell(Cell(canvas, 3, 3, 5))
    try:
        p.add_cell(Cell(canvas, 1, 3, 5))
        assert False
    except AssertionError:
        pass

    print("All unit tests passed.")
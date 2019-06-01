__wave_manager = None
def getWaveManager():
    from WaveClasses import AbstractWave, RandomWave, WaveFromFile
    from InvaderClasses import AbstractInvader
    from interface import implements
    from Subject_Observer import Subject, Observer

    class WaveManager(implements(Subject), implements(Observer)):
        def __init__(self):
            self._canvas = None
            self._minimum_waves = 10
            self._wave_list = []
            self._waves_left = True
            self._active_invaders_list = []
            self._active_waves = []
            self._observers_list = []
            self._changed = False
            self._changed_invader = None
            self._depleted = False

        def setCanvas(self, canvas):
            if self._canvas == None: self._canvas = canvas
        def initializeWaves(self):
            self._wave_list = []
            self.readWaves()

        def readWaves(self):
            with open("waves/all_waves.txt") as allwaves:
                for elem in allwaves:
                    self.addWave(self.readWaveInfo(elem.strip()))
            #if less than ten waves are read, fill in up to ten waves with random waves
            if len(self._wave_list) < self._minimum_waves:
                for filler_wave in range (self._minimum_waves-len(self._wave_list)):
                    random_wave = RandomWave(self._canvas, 1000, num_invaders=15)
                    self.addWave(random_wave)

        def readWaveInfo(self, file_name):
            '''Read wave contents from a file and create a wave'''
            wave = WaveFromFile(self._canvas, 1000) #one second offset
            if file_name == "TrafficJam.txt": wave.setOffset(1600)
            with open("waves/%s" % file_name) as wf:
                # print("reading from waves/%s..." % file_name)     #USE THIS FOR PATH_READING DEBUGGING
                for line in wf:
                    line_split = line.split('\n')
                    invader = line_split[0]
                    wave.addInvader(invader)
            return wave

    
        '''for dealing with deployed (active) waves'''
        def setAllActiveInvaders(self):
            self._active_invaders_list = []
            for wave in self._active_waves:
                for invader in wave.getInvaders():
                    self._active_invaders_list.append(invader)
        def getActiveWaves(self):
            return self._active_waves
        def getActiveInvaders(self):
            return self._active_invaders_list
        def addActiveInvader(self, invader):
            self._active_invaders_list.append(invader)
            self._active_invaders_left = True
        def removeActiveInvader(self, invader):
            self._active_invaders_list.remove(invader)
            if (self._active_invaders_list == []) and (not self._waves_left):
                self._depleted = True
                self.setChanged()

    
        '''for dealing with non-deployed waves'''
        def getRemainingWaves(self):
            return self._wave_list
        def addWave(self, wave):
            self._wave_list.append(wave)
            wave.registerObserver(self)
        def removeWave(self, wave):
            self._wave_list.remove(wave)
        def deployWave(self):
            if len(self._wave_list) != 0:
                wave = self._wave_list[0]
                print("Start next wave now...")
                wave.deployInvaders()
                self._active_waves.append(wave)
                self._wave_list.remove(wave)
            else:
                if (len(self._active_invaders_list) == 0):
                    self.setChanged()

    
        '''Methods for the Wave Manager as a Subject of App'''
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
            if self.isChanged():
                if self._depleted == False:
                    for observer in self._observers_list:
                        observer.update(self._changed_invader)
                else:
                    for observer in self._observers_list:
                        observer.update(self)
    
        '''Wave Manager as an Observer of Wave'''
        def update(self, changed_thing):
            if isinstance(changed_thing, AbstractWave):
                self.processWave(changed_thing)
            elif isinstance(changed_thing, AbstractInvader):
                self.processInvader(changed_thing)

        def processWave(self, wave):
            self._active_waves.remove(wave)
            wave.__delete__()
            if self._wave_list == []:
                self._waves_left = False
                if self._active_invaders_list == []:
                    self.setChanged()
        def processInvader(self, invader):
            if not invader.isAlive():
                self.removeActiveInvader(invader)


        def __delete__(self):
            for wave in self._active_waves:
                wave.__delete__()
            for wave in self._wave_list:
                wave.__delete__()
            for invader in self._active_invaders_list:
                invader.quickDelete()
            del self

    global __wave_manager
    if __wave_manager == None:
        __wave_manager = WaveManager()
    return __wave_manager
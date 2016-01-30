
from pymjin2 import *

MAIN_BALL_NAME       = "ball"
MAIN_BALLS_NB        = 8
MAIN_CLEANER_NAME    = "cleaner"
MAIN_LEVEL_NAME      = "level"
MAIN_LEVELS_NB       = 8
MAIN_POINT_NAME      = "point"
MAIN_TRACK_NAME      = "track"
MAIN_SOUND_SELECTION = "soundBuffer.default.selection"
# Hard coded values. Ugly. Should be a separate component.
MAIN_START_ACTION    = "spawn.default.start"
MAIN_START_CAMERA    = "camera"
MAIN_START_SOUND     = "soundBuffer.default.start"

class MainImpl(object):
    def __init__(self, client):
        # Refer.
        self.c = client
        # Create.
        self.currentLevel     = None
        self.intialBallPos    = None
        self.ballAvailability = None
        self.cleanerPicking   = None
        self.ballIsCatched    = False
        self.ballsLeft        = MAIN_BALLS_NB
        self.ballsCatched     = 0
        self.introIsOn         = False
    def __del__(self):
        # Derefer.
        self.c = None
    def onBallAccessible(self, key, value):
        val = self.currentLevel if value[0] == "1" else None
        self.ballAvailability = val
        if (self.ballAvailability is not None):
            self.tryToCatch()
    def onCleanerPicking(self, key, value):
        val = value[0] if (len(value[0])) else None
        self.cleanerPicking = val
        if (self.cleanerPicking is not None):
            self.tryToCatch()
    def onBallStopped(self, key, value):
        # Only proceed if this is a normal ball rolling.
        # If it has been catched, don't proceed.
        if (not self.ballIsCatched):
            self.step()
    def onCleanerSwallow(self, key, value):
        # Finished swallowing. Restart the ball sequence.
        if (value[0] == ""):
            if (self.processBall()):
                self.restartBallSequence()
    def onGameStart(self, key, value):
        print "Starting the game"
        self.initialBallPos = self.c.get("node.$SCENE.$BALL.position")[0]
        self.currentLevel = 0
        self.step()
    def onIntroStart(self, key, value):
        if (self.introIsOn):
            return
        self.introIsOn = True
        # Start the 'start' action.
        self.c.set("$START.$SCENE.$CAMERA.active", "1")
        self.c.set("$SNDSTART.state", "play")
    def onTrackSelection(self, key, value):
        id = key[2].replace(MAIN_TRACK_NAME, "")
        self.c.set("$SNDSELECTION.state", "play")
        self.c.set("$CLEANER.$SCENE.$CLEANER.catch", MAIN_POINT_NAME + id)
        #self.performCatch()
    def performCatch(self):
        self.ballIsCatched = True
        # Stop the ball.
        self.c.set("$BALL.$SCENE.$BALL.moving", "0")
        # Swallow it.
        self.c.set("$CLEANER.$SCENE.$CLEANER.swallow", MAIN_BALL_NAME)
    def processBall(self):
        self.ballsLeft = self.ballsLeft - 1
        print "Balls left:", self.ballsLeft
        if (self.ballsLeft < 1):
            print "No more balls to catch. The game is over"
            print "Stats: balls catched / overall: {0} / {1}".format(self.ballsCatched,
                                                                     MAIN_BALLS_NB)
            if (self.ballsCatched == MAIN_BALLS_NB):
                print "YOU WON"
            else:
                print "YOU LOST"
            return False
        return True
    def restartBallSequence(self):
        #print "Restarting the ball sequence"
        self.ballAvailability = None
        self.cleanerPicking = None
        self.ballIsCatched = False
        self.currentLevel = 0
        self.step()
    def step(self):
        self.currentLevel = self.currentLevel + 1
        if (self.currentLevel > MAIN_LEVELS_NB):
            #print "The ball has stopped, no more levels to go"
            if (self.processBall()):
                self.restartBallSequence()
            return
        #print "Moving the ball down the level", self.currentLevel
        levelName = MAIN_LEVEL_NAME + str(self.currentLevel)
        self.c.set("node.$SCENE.$BALL.parent",   levelName)
        self.c.set("node.$SCENE.$BALL.position", self.initialBallPos)
        self.c.set("$BALL.$SCENE.$BALL.moving", "1")
    def tryToCatch(self):
        if ((self.ballAvailability is not None) and
            (self.cleanerPicking is not None)):
            if (self.cleanerPicking.endswith(str(self.ballAvailability))):
                self.performCatch()
                self.ballsCatched = self.ballsCatched + 1
                #print "catched the ball at point {0}. ".format(self.ballAvailability)
                print "Balls catched / left: {0} / {1}".format(self.ballsCatched,
                                                               self.ballsLeft)

class Main(object):
    def __init__(self, sceneName, nodeName, env):
        # Create.
        self.c    = EnvironmentClient(env, "Main")
        self.impl = MainImpl(self.c)
        # Prepare.
        self.c.setConst("BALL",         MAIN_BALL_NAME)
        self.c.setConst("CLEANER",      MAIN_CLEANER_NAME)
        self.c.setConst("SCENE",        sceneName)
        self.c.setConst("SNDSELECTION", MAIN_SOUND_SELECTION)
        # Ugly hard coded values.
        self.c.setConst("START",        MAIN_START_ACTION)
        self.c.setConst("CAMERA",       MAIN_START_CAMERA)
        self.c.setConst("SNDSTART",     MAIN_START_SOUND)
        # Listen to ball motion finish.
        self.c.listen("$BALL.$SCENE.$BALL.moving", "0", self.impl.onBallStopped)
        # Listen to ball accessibility.
        self.c.listen("$BALL.$SCENE.$BALL.accessible", None, self.impl.onBallAccessible)
        # Listen to track selections.
        self.c.listen("node.$SCENE..selected", "1", self.impl.onTrackSelection)
        # Listen to cleaner picking.
        self.c.listen("$CLEANER.$SCENE.$CLEANER.picking", None, self.impl.onCleanerPicking)
        # Listen to cleaner swallow.
        self.c.listen("$CLEANER.$SCENE.$CLEANER.swallow", "", self.impl.onCleanerSwallow)
        # Listen to the SPACE key to start the game.
        self.c.listen("input.SPACE.key", "1", self.impl.onIntroStart)
        # Listen to the 'start' action finish.
        self.c.listen("$START.$SCENE.$CAMERA.active", "0", self.impl.onGameStart)
        print "{0} Main.__init__({1}, {2})".format(id(self), sceneName, nodeName)
    def __del__(self):
        # Tear down.
        self.c.clear()
        # Destroy
        del self.impl
        del self.c
        print "{0} Main.__del__".format(id(self))

def SCRIPT_CREATE(sceneName, nodeName, env):
    return Main(sceneName, nodeName, env)

def SCRIPT_DESTROY(instance):
    del instance


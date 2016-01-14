
from pymjin2 import *

MAIN_BALL_NAME    = "ball"
MAIN_CLEANER_NAME = "cleaner"
MAIN_LEVEL_NAME   = "level"
MAIN_LEVELS_NB    = 8
MAIN_POINT_NAME   = "point"
MAIN_TRACK_NAME   = "track"

class MainImpl(object):
    def __init__(self, client):
        # Refer.
        self.c = client
        # Create.
        self.currentLevel  = None
        self.intialBallPos = None
    def __del__(self):
        # Derefer.
        self.c = None
    def onBallStopped(self, key, value):
        self.step()
    def onFinishedLoading(self, key, value):
        print "Starting the game"
        self.initialBallPos = self.c.get("node.$SCENE.$BALL.position")[0]
        self.currentLevel = 0
        self.step()
    def onTrackSelection(self, key, value):
        id = key[2].replace(MAIN_TRACK_NAME, "")
        self.c.set("$CLEANER.$SCENE.$CLEANER.orientation", MAIN_POINT_NAME + id)
    def step(self):
        self.currentLevel = self.currentLevel + 1
        if (self.currentLevel > MAIN_LEVELS_NB):
            print "The ball has stopped, no more levels to go"
            return
        #print "Moving the ball down the level", self.currentLevel
        levelName = MAIN_LEVEL_NAME + str(self.currentLevel)
        self.c.set("node.$SCENE.$BALL.parent",   levelName)
        self.c.set("node.$SCENE.$BALL.position", self.initialBallPos)
        self.c.set("$BALL.$SCENE.$BALL.moving", "1")

class Main(object):
    def __init__(self, sceneName, nodeName, env):
        # Create.
        self.c    = EnvironmentClient(env, "Main")
        self.impl = MainImpl(self.c)
        # Prepare.
        self.c.setConst("BALL",    MAIN_BALL_NAME)
        self.c.setConst("CLEANER", MAIN_CLEANER_NAME)
        self.c.setConst("SCENE",   sceneName)
        # Listen to scene loading finish.
        self.c.listen("scene.opened", None, self.impl.onFinishedLoading)
        # Listen to ball motion finish.
        self.c.listen("$BALL.$SCENE.$BALL.moving", "0", self.impl.onBallStopped)
        # Listen to track selections.
        self.c.listen("node.$SCENE..selected", "1", self.impl.onTrackSelection)
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


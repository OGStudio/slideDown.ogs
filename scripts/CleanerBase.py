
from pymjin2 import *

CLEANER_NAME          = "cleaner"
CLEANER_ACTION        = "spawn.default.orientCleaner"
CLEANER_ACTION_ROTATE = "rotate.default.rotateCleaner"
CLEANER_SPEED         = "5000"
#BALL_SOUND        = "soundBuffer.default.rolling"

class CleanerBaseImpl(object):
    def __init__(self, client):
        # Refer.
        self.c = client
        # Create.
        self.isMoving = False
        self.orientation = ""
    def __del__(self):
        # Derefer.
        self.c = None
    def onFinish(self, key, value):
        self.isMoving = False
        print "Cleaner.onFinish", key, value
#        self.c.set("$SOUND.state", "stop")
#        self.c.report("$TYPE.$SCENE.$NODE.moving", "0")
    def setOrientation(self, key, value):
        if (self.isMoving):
            return
        if (self.orientation == value[0]):
            return
        self.orientation = value[0]
        print "setOrientation", key, value
        self.isMoving = True
        self.c.setConst("POINT", value[0])
        pos = self.c.get("node.$SCENE.$POINT.positionAbs")[0]
        rot = self.c.get("node.$SCENE.$POINT.rotationAbs")[0]
        # Setup action points.
        self.c.set("$ROTATE.point", CLEANER_SPEED + " " + rot)
        # Start the action.
        self.c.set("$ORIENT.$SCENE.$NODE.active", "1")
        #self.c.set("$SOUND.state", "play")

class CleanerBase(object):
    def __init__(self, sceneName, nodeName, env):
        # Create.
        name      = "CleanerBase/{0}/{1}".format(sceneName, nodeName)
        self.c    = EnvironmentClient(env, name)
        self.impl = CleanerBaseImpl(self.c)
        # Prepare.
        self.c.setConst("CLEANER", CLEANER_NAME)
        self.c.setConst("SCENE",   sceneName)
        self.c.setConst("NODE",    nodeName)
        self.c.setConst("ORIENT",  CLEANER_ACTION)
        self.c.setConst("ROTATE",  CLEANER_ACTION_ROTATE)
        #self.c.setConst("SOUND", BALL_SOUND)
        # Provide "orientation".
        self.c.provide("$CLEANER.$SCENE.$CLEANER.orientation",
                       self.impl.setOrientation)
        # Listen to action finish.
        self.c.listen("$ORIENT.$SCENE.$NODE.active", "0", self.impl.onFinish)
    def __del__(self):
        # Tear down.
        self.c.clear()
        # Destroy
        del self.impl
        del self.c

def SCRIPT_CREATE(sceneName, nodeName, env):
    return CleanerBase(sceneName, nodeName, env)

def SCRIPT_DESTROY(instance):
    del instance



from pymjin2 import *

CLEANER_ACTION        = "sequence.default.catch"
CLEANER_ACTION_MOVE   = "move.default.mPositionCleaner"
CLEANER_ACTION_PICK   = "delay.default.waitForCleanerToCatch"
CLEANER_ACTION_ROTATE = "rotate.default.rPositionCleaner"
CLEANER_NAME          = "cleaner"
#BALL_SOUND        = "soundBuffer.default.rolling"

class CleanerImpl(object):
    def __init__(self, client):
        # Refer.
        self.c = client
        # Create.
        self.isMoving = False
        self.orientation = ""
        self.speed = None
    def __del__(self):
        # Derefer.
        self.c = None
    def setCatch(self, key, value):
        if (self.isMoving):
            return
        self.orientation = value[0]
        self.isMoving = True
        self.c.setConst("POINT", value[0])
        # Position
        pos = self.c.get("node.$SCENE.$POINT.positionAbs")[0]
        ppos = pos.split(" ")
        pos = self.c.get("node.$SCENE.$CLEANER.position")[0]
        cpos = pos.split(" ")
        pos = "{0} {1} {2}".format(cpos[0], cpos[1], ppos[2])
        # Get speed from the actions' setup.
        if (not self.speed):
            p = self.c.get("$MOVE.point")
            self.speed = p[0].split(" ")[0]
        # Rotation.
        rot = self.c.get("node.$SCENE.$POINT.rotationAbs")[0]
        # Setup action points.
        self.c.set("$ROTATE.point", self.speed + " " + rot)
        # Only position height.
        self.c.set("$MOVE.point",   self.speed + " " + pos)
        # Start the action.
        self.c.set("$CATCH.$SCENE.$NODE.active", "1")
        #self.c.set("$SOUND.state", "play")
    def onFinish(self, key, value):
        self.isMoving = False
        print "Cleaner.onFinish", key, value
#        self.c.set("$SOUND.state", "stop")
#        self.c.report("$TYPE.$SCENE.$NODE.moving", "0")
    def onPicking(self, key, value):
        val = self.orientation if value[0] == "1" else ""
        self.c.report("$CLEANER.$SCENE.$CLEANER.picking", val)

class Cleaner(object):
    def __init__(self, sceneName, nodeName, env):
        # Create.
        name      = "Cleaner/{0}/{1}".format(sceneName, nodeName)
        self.c    = EnvironmentClient(env, name)
        self.impl = CleanerImpl(self.c)
        # Prepare.
        self.c.setConst("CLEANER", CLEANER_NAME)
        self.c.setConst("SCENE",   sceneName)
        self.c.setConst("NODE",    nodeName)
        self.c.setConst("CATCH",   CLEANER_ACTION)
        self.c.setConst("MOVE",    CLEANER_ACTION_MOVE)
        self.c.setConst("PICK",    CLEANER_ACTION_PICK)
        self.c.setConst("ROTATE",  CLEANER_ACTION_ROTATE)
        #self.c.setConst("SOUND", BALL_SOUND)
        # Provide "catch".
        self.c.provide("$CLEANER.$SCENE.$CLEANER.catch", self.impl.setCatch)
        # Provide "picking".
        self.c.provide("$CLEANER.$SCENE.$CLEANER.picking")
        # Listen to catch action finish.
        self.c.listen("$CATCH.$SCENE.$NODE.active", "0", self.impl.onFinish)
        # Listen to picking action.
        self.c.listen("$PICK.$SCENE.$NODE.active", None, self.impl.onPicking)
    def __del__(self):
        # Tear down.
        self.c.clear()
        # Destroy
        del self.impl
        del self.c

def SCRIPT_CREATE(sceneName, nodeName, env):
    return Cleaner(sceneName, nodeName, env)

def SCRIPT_DESTROY(instance):
    del instance


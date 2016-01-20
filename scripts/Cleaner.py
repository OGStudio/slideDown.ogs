
from pymjin2 import *

CLEANER_ACTION         = "sequence.default.catch"
CLEANER_ACTION_MOVE    = "move.default.mPositionCleaner"
CLEANER_ACTION_PICK    = "delay.default.waitForCleanerToCatch"
CLEANER_ACTION_ROTATE  = "rotate.default.rPositionCleaner"
CLEANER_ACTION_SWALLOW = "move.default.swallowBall"
CLEANER_NAME           = "cleaner"
#BALL_SOUND        = "soundBuffer.default.rolling"

class CleanerImpl(object):
    def __init__(self, client):
        # Refer.
        self.c = client
        # Create.
        self.isMoving = False
        self.orientation = ""
        self.speed = None
        self.swallowSpeed = None
    def __del__(self):
        # Derefer.
        self.c = None
    def onFinish(self, key, value):
        self.isMoving = False
#        print "Cleaner.onFinish", key, value
#        self.c.set("$SOUND.state", "stop")
#        self.c.report("$TYPE.$SCENE.$NODE.moving", "0")
    def onPicking(self, key, value):
        val = self.orientation if value[0] == "1" else ""
        self.c.report("$CLEANER.$SCENE.$CLEANER.picking", val)
    def onSwallowed(self, key, value):
        self.c.report("$CLEANER.$SCENE.$CLEANER.swallow", "")
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
        if (self.speed is None):
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
    def setSwallow(self, key, value):
        # Get speed from the actions' setup.
        if (self.swallowSpeed is None):
            p = self.c.get("$SWALLOW.point")
            self.swallowSpeed = p[0].split(" ")[0]
        #print "speed", self.swallowSpeed
        self.c.setConst("BALL", value[0])
        # Ball position.
        bpos = self.c.get("node.$SCENE.$BALL.positionAbs")[0]
        # Detach the ball from the parent.
        self.c.set("node.$SCENE.$BALL.parent", "ROOT")
        self.c.set("node.$SCENE.$BALL.position", bpos)
        # Cleaner position.
        cpos = self.c.get("node.$SCENE.$CLEANER.positionAbs")[0]
        # Setup action points.
        points = []
        points.append("0 " + bpos)
        points.append(self.swallowSpeed + " " + cpos)
        self.c.set("$SWALLOW.point", points)
        # Start the action.
        self.c.set("$SWALLOW.$SCENE.$BALL.active", "1")

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
        self.c.setConst("SWALLOW", CLEANER_ACTION_SWALLOW)
        #self.c.setConst("SOUND", BALL_SOUND)
        # Provide "catch".
        self.c.provide("$CLEANER.$SCENE.$CLEANER.catch", self.impl.setCatch)
        # Provide "picking".
        self.c.provide("$CLEANER.$SCENE.$CLEANER.picking")
        # Provide "swallow".
        self.c.provide("$CLEANER.$SCENE.$CLEANER.swallow", self.impl.setSwallow)
        # Listen to catch action finish.
        self.c.listen("$CATCH.$SCENE.$NODE.active", "0", self.impl.onFinish)
        # Listen to picking action.
        self.c.listen("$PICK.$SCENE.$NODE.active", None, self.impl.onPicking)
        # Listen to swallow action.
        self.c.listen("$SWALLOW.$SCENE..active", "0", self.impl.onSwallowed)
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



from pymjin2 import *

BALL_TYPE          = "ball"
#BALL_ACTION_ACCESS = "spawn.default.bottomForwardCatch"
BALL_ACTION_ACCESS = "move.default.moveBottomForwardCatch"
BALL_ACTION_TRACK  = "sequence.default.track"
BALL_SOUND         = "soundBuffer.default.rolling"

class BallImpl(object):
    def __init__(self, client):
        # Refer.
        self.c = client
        # Create.
        self.isMoving = False
    def __del__(self):
        # Derefer.
        self.c = None
    def onAccess(self, key, value):
        self.c.report("$TYPE.$SCENE.$NODE.accessible", value[0])
    def onFinish(self, key, value):
        self.isMoving = False
        self.c.set("$SOUND.state", "stop")
        self.c.report("$TYPE.$SCENE.$NODE.moving", "0")
    def setMoving(self, key, value):
        self.isMoving = (value[0] == "1")
        self.c.set("$TRACK.$SCENE.$NODE.active",
                   "1" if self.isMoving else "0")
        self.c.set("$SOUND.state",
                   "play" if self.isMoving else "stop")

class Ball(object):
    def __init__(self, sceneName, nodeName, env):
        # Create.
        name      = "Ball/{0}/{1}".format(sceneName, nodeName)
        self.c    = EnvironmentClient(env, name)
        self.impl = BallImpl(self.c)
        # Prepare.
        self.c.setConst("TYPE",   BALL_TYPE)
        self.c.setConst("SCENE",  sceneName)
        self.c.setConst("NODE",   nodeName)
        self.c.setConst("ACCESS", BALL_ACTION_ACCESS)
        self.c.setConst("TRACK",  BALL_ACTION_TRACK)
        self.c.setConst("SOUND",  BALL_SOUND)
        # Provide "moving".
        self.c.provide("$TYPE.$SCENE.$NODE.moving", self.impl.setMoving)
        # Provide "accessible".
        self.c.provide("$TYPE.$SCENE.$NODE.accessible")
        # Listen to track action to report 'moving' finish.
        self.c.listen("$TRACK.$SCENE.$NODE.active", "0", self.impl.onFinish)
        # Listen to catch action to report 'accessible' state.
        self.c.listen("$ACCESS.$SCENE.$NODE.active", None, self.impl.onAccess)
        print "{0} Ball.__init__({1}, {2})".format(id(self), sceneName, nodeName)
    def __del__(self):
        # Tear down.
        self.c.clear()
        # Destroy
        del self.impl
        del self.c
        print "{0} Ball.__del__".format(id(self))

def SCRIPT_CREATE(sceneName, nodeName, env):
    return Ball(sceneName, nodeName, env)

def SCRIPT_DESTROY(instance):
    del instance


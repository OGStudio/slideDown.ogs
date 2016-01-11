
from pymjin2 import *

BALL_TYPE         = "ball"
BALL_ACTION_TRACK = "sequence.default.track"

class BallImpl(object):
    def __init__(self, client):
        # Refer.
        self.c = client
        # Create.
        self.isMoving = False
    def __del__(self):
        # Derefer.
        self.c = None
    def onFinish(self, key, value):
        self.isMoving = False
        self.c.report("$TYPE.$SCENE.$NODE.moving", "0")
    def setMoving(self, key, value):
        self.isMoving = True
        self.c.set("$TRACK.$SCENE.$NODE.active", "1")

class Ball(object):
    def __init__(self, sceneName, nodeName, env):
        # Create.
        name      = "Ball/{0}/{1}".format(sceneName, nodeName)
        self.c    = EnvironmentClient(env, name)
        self.impl = BallImpl(self.c)
        # Prepare.
        self.c.setConst("TYPE",  BALL_TYPE)
        self.c.setConst("SCENE", sceneName)
        self.c.setConst("NODE",  nodeName)
        self.c.setConst("TRACK", BALL_ACTION_TRACK)
        # Provide "moving".
        self.c.provide("$TYPE.$SCENE.$NODE.moving", self.impl.setMoving)
        # Listen to action to report 'moving' finish.
        self.c.listen("$TRACK.$SCENE.$NODE.active", "0", self.impl.onFinish)
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


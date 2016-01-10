
from pymjin2 import *

BALL_TYPE               = "ball"
BALL_ACTION_TOP_FORWARD = "move.default.moveTopForward"

class BallImpl(object):
    def __init__(self, client):
        # Refer.
        self.c = client
        # Create.
        self.isMoving = False
    def __del__(self):
        # Derefer.
        self.c = None
    def setMoving(self, key, value):
        print "ball.setMoving", key, value
        self.isMoving = True
        self.c.set("$TOPFWD.$SCENE.$NODE.active", "1")

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
        self.c.setConst("TOPFWD", BALL_ACTION_TOP_FORWARD)
        # Provide "moving".
        self.c.provide("$TYPE.$SCENE.$NODE.moving", self.impl.setMoving)
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


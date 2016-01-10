
from pymjin2 import *

MAIN_BALL_NAME = "ball"

class MainImpl(object):
    def __init__(self, client):
        # Refer.
        self.c = client
    def __del__(self):
        # Derefer.
        self.c = None
    def onFinishedLoading(self, key, value):
        print "Starting the game"
        self.step()
    def step(self):
        print "Moving the ball forward"
        self.c.set("$BALL.$SCENE.$BALL.moving", "1")

class Main(object):
    def __init__(self, sceneName, nodeName, env):
        # Create.
        self.c    = EnvironmentClient(env, "Main")
        self.impl = MainImpl(self.c)
        # Prepare.
        self.c.setConst("BALL",  MAIN_BALL_NAME)
        self.c.setConst("SCENE", sceneName)
        # Listen to scene loading finish.
        self.c.listen("scene.opened", None, self.impl.onFinishedLoading)
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


from twisted.web import resource

from prospector.resources import config

def getRoot():
    root = resource.Resource()
    root.putChild("config", config.getConfigResource())

    return root

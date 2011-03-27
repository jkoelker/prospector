from twisted.web import resource

from prospector.resources import config
from prospector.resources import deploy

def getRoot():
    root = resource.Resource()
    root.putChild("config", config.getConfigResource())
    root.putChild("deploy",  deploy.Deploy())

    return root

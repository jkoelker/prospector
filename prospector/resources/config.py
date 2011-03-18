from zope.interface import implements

from twisted.cred import checkers, portal
from twisted.web import guard, resource, static

from prospector import const

class ConfigRealm(object):
    implements(portal.IRealm)

    def requestAvatar(self, avatarId, mind, *interfaces):
        if resource.IResource in interfaces:
            return (resource.IResource,
                    static.File(const.CONFIGPATH),
                    lambda: None)
            raise NotImplementedError()

def getConfigResource():
    creds = {const.USER: const.SESAME}
    checker = checkers.InMemoryUsernamePasswordDatabaseDontUse(**creds)
    configPortal = portal.Portal(ConfigRealm(), [checker])
    factory = guard.DigestCredentialFactory("md5", "config")
    return guard.HTTPAuthSessionWrapper(configPortal, [factory])


from zope.interface import implements

from twisted.python import usage, log
from twisted.plugin import IPlugin
from twisted.application.service import IServiceMaker
from twisted.application import internet, service, strports

from twisted.cred import checkers, portal
from twisted.conch.manhole_ssh import ConchFactory, TerminalRealm
from twisted.conch.manhole_tap import chainedProtocolFactory

from twisted.internet import ssl
from twisted.web import server

from prospector import web, const

creds = {"admin": "p"}

class Options(usage.Options):
    optParameters = [["ssh", "s", 2222, "The port number for ssh shell."],
                     ["web", "w", 8443, "The port number for the web."]]

class ProspectorServiceMaker(object):
    implements(IServiceMaker, IPlugin)
    tapname = "prospector"
    description = "Prospector sets up the mine(craft)"
    options = Options

    def makeService(self, options):
        svc = service.MultiService()

        checker = checkers.InMemoryUsernamePasswordDatabaseDontUse(**creds)

        namespace = {}

        sshRealm = TerminalRealm()
        sshRealm.chainedProtocolFactory = chainedProtocolFactory(namespace)

        sshPortal = portal.Portal(sshRealm, [checker])
        sshFactory = ConchFactory(sshPortal)
        sshService = strports.service(str(options["ssh"]), sshFactory)
        sshService.setServiceParent(svc)

        site = server.Site(web.getRoot(), logPath=const.WEBLOG)
        sslFactory = ssl.DefaultOpenSSLContextFactory(const.SSLKEY,
                                                      const.SSLCERT)
        sslServer = internet.SSLServer(int(options["web"]),
                                       site,
                                       sslFactory)
        sslServer.setServiceParent(svc)

        return svc

serviceMaker = ProspectorServiceMaker()



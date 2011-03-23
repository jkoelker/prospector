
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

from prospector import web, settings, provision

creds = {'admin': 'pkxmen0w'}

class Options(usage.Options):
    optParameters = [
        ["file", "f", settings.DEFAULT_CONFIG_FILE,
         "The config file to use [%s]." % settings.DEFAULT_CONFIG_FILE],]

class ProspectorServiceMaker(object):
    implements(IServiceMaker, IPlugin)
    tapname = "prospector"
    description = "Prospector sets up the mine(craft)"
    options = Options

    def makeService(self, options):
        settings.loadConfig(options["file"])

        svc = service.MultiService()

        checker = checkers.InMemoryUsernamePasswordDatabaseDontUse(**creds)

        namespace = {"host": "67.23.43.147",
                     "user": "root",
                     "pw": "pkxmen0w",
                     "provision": provision}

        sshRealm = TerminalRealm()
        sshRealm.chainedProtocolFactory = chainedProtocolFactory(namespace)

        sshPortal = portal.Portal(sshRealm, [checker])
        sshFactory = ConchFactory(sshPortal)
        sshService = strports.service(str(settings.config["ssh"]["port"]),
                                      sshFactory)
        sshService.setServiceParent(svc)

        site = server.Site(web.getRoot(),
                           logPath=settings.config["web"]["log"])

        if int(settings.config["web"]["port"]) != 0:
            siteService = strports.service(settings.config["web"]["port"],
                                           site)
            siteService.setServiceParent(svc)

        if int(settings.config["web"]["sslport"]) != 0:
            key = settings.config["web"]["key"]
            cert = settings.config["web"]["cert"]
            port = int(settings.config["web"]["sslport"])

            sslFactory = ssl.DefaultOpenSSLContextFactory(key, cert)
            sslServer = internet.SSLServer(port, site, sslFactory)
            sslServer.setServiceParent(svc)

        return svc

serviceMaker = ProspectorServiceMaker()



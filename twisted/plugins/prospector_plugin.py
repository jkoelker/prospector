
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

from OpenSSL import SSL

creds = {'admin': 'pkxmen0w'}

class ChainedOpenSSLContextFactory(ssl.DefaultOpenSSLContextFactory):
    def __init__(self, privateKeyFileName, certificateChainFileName,
                 sslmethod=SSL.SSLv23_METHOD, _contextFactory=SSL.Context):
        """
        @param privateKeyFileName: Name of a file containing a private key
        @param certificateChainFileName: Name of a file containing a certificate chain
        @param sslmethod: The SSL method to use
        """
        self.privateKeyFileName = privateKeyFileName
        self.certificateChainFileName = certificateChainFileName
        self.sslmethod = sslmethod
        self._contextFactory = _contextFactory

        self.cacheContext()
    
    def cacheContext(self):
        if self._context is None:
            ctx = self._contextFactory(self.sslmethod)
            # Disallow SSLv2!  It's insecure!  SSLv3 has been around since
            # 1996.  It's time to move on.
            ctx.set_options(SSL.OP_NO_SSLv2)
            ctx.use_certificate_chain_file(self.certificateChainFileName)
            ctx.use_privatekey_file(self.privateKeyFileName)
            self._context = ctx

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

            sslFactory = ChainedOpenSSLContextFactory(key, cert)
            sslServer = internet.SSLServer(port, site, sslFactory)
            sslServer.setServiceParent(svc)

        return svc

serviceMaker = ProspectorServiceMaker()



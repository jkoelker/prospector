
from zope.interface import implements

from twisted.python import usage, log, failure
from twisted.plugin import IPlugin
from twisted.application.service import IServiceMaker
from twisted.application import internet, service, strports

from twisted.cred import credentials, checkers, portal
from twisted.conch.manhole_ssh import ConchFactory, TerminalRealm
from twisted.conch.manhole_tap import chainedProtocolFactory
from twisted.conch.ssh import keys
from twisted.conch import error

from twisted.internet import ssl
from twisted.web import server

from prospector import web, settings, provision

from OpenSSL import SSL
import base64

pubAuthKeys = {"admin": "AAAAB3NzaC1yc2EAAAADAQABAAABAQDG3Rx6KpTyu5Hr3sjg3BHF/TyTKLxCTV9pxFCL5ISEv1f2BUBkmhhkD8AmPJBwByVcjgNvTnNV4WpQbY69KfHgolEe68BWXMGH7Db/wYZdFluHy2kM38lgxpC1FMon1qBEC4uh+BI0Xvowl9BwuDGwStwJlaxtxqsOZu7FvPhZ2j01aQXLK3lYss0mYDHaee4NIGKAHs1Co8LKhAu6T8EJ/7n1Phnh0E80BCwnw4RldBgBchLtwQhLUIFkPbQsijjSNVOMbwhrMzST7A2+bZvstZzLIqeSymHlfmhRoVrWk11MHClH4GYM/Sl0ootWrPLlW9oGipcLKxnOQLWzOQnx"}

class PublicKeyCredentialsChecker:
    implements(checkers.ICredentialsChecker)
    credentialInterfaces = (credentials.ISSHPrivateKey,)

    def __init__(self, authKeys):
        self.authKeys = authKeys

    def requestAvatarId(self, creds):
        if creds.username in self.authKeys:
            userKey = self.authKeys[creds.username]
            if not creds.blob == base64.decodestring(userKey):
                raise failure.Failure(error.ConchError("Unrecognized key"))
            if not creds.signature:
                return failure.Failure(error.ValidPublicKey())
            pubKey = keys.Key.fromString(data=creds.blob)
            if pubKey.verify(creds.signature, creds.sigData):
                return creds.username 
            else:
                return failure.Failure(error.ConchError("Incorrect signature"))
        else:
            return failure.Failure(error.ConchError("No such user"))
            

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

        checker = PublicKeyCredentialsChecker(pubAuthKeys)

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



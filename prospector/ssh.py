from twisted.conch.ssh import transport, userauth, connection
from twisted.conch.ssh import common, channel
from twisted.conch.ssh.keys import Key
from twisted.internet import defer, reactor, protocol

class Transport(transport.SSHClientTransport):
    def __init__(self, deferConnectionSecure):
        self.deferConnectionSecure = deferConnectionSecure

    def verifyHostKey(self, hostKey, fingerprint):
        return defer.succeed(True)

    def connectionSecure(self):
        self.deferConnectionSecure.callback(self)

class PasswordAuth(userauth.SSHUserAuthClient):
    def __init__(self, username, password, conn):
        userauth.SSHUserAuthClient.__init__(self, username, conn)
        self.password = password

    def getPassword(self, prompt=None):
        return defer.succeed(self.password)

class CommandConnection(connection.SSHConnection):
    def __init__(self, deferServiceStarted):
        connection.SSHConnection.__init__(self)
        self.deferServiceStarted = deferServiceStarted

    def serviceStarted(self):
        self.deferServiceStarted.callback(self)

class CommandChannel(channel.SSHChannel):
    name = "session"

    def __init__(self, command, deferStdOut, deferStdErr, *args, **kwargs):
        channel.SSHChannel.__init__(self, *args, **kwargs)
        self.command = command
        self.deferStdOut = deferStdOut
        self.deferStdErr = deferStdErr
        self.out = ''
        self.err = ''

    def channelOpen(self, _):
        req = self.conn.sendRequest(self, "exec", common.NS(self.command),
                                    wantReply=True)
        req.addCallback(lambda _: self.conn.sendEOF(self))

    def dataReceived(self, data):
        self.out = self.out + data

    def extReceived(self, dataType, data):
        if dataType == 1:
            self.err = self.err + data

    def eofReceived(self):
        if self.deferStdOut is not None:
            self.deferStdOut.callback(self.out)
        if self.deferStdErr is not None:
            self.deferStdErr.callback(self.err)

class TransportFactory(protocol.ClientFactory):
    def __init__(self, deferTransportReady):
        self.deferTransportReady = deferTransportReady

    def buildProtocol(self, addr):
        return Transport(self.deferTransportReady)

def passwordAuth(transport, username, password):
    connectionReady = defer.Deferred()
    conn = CommandConnection(connectionReady)
    transport.requestService(PasswordAuth(username, password, conn))
    return connectionReady

def connect(host, username, password, port=22):
    connection = defer.Deferred()
    connection.addCallback(passwordAuth, username, password)
    reactor.connectTCP(host, port, TransportFactory(connection))
    return connection

def sendCommand(connection, command, deferStdOut=None, deferStdErr=None):
    channel = CommandChannel(command, deferStdOut, deferStdErr,
                             conn=connection)
    connection.openChannel(channel)
    return connection

def disconnect(connection):
    connection.transport.loseConnection()

    

        

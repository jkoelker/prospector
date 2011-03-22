from twisted.conch.error import ConchError
from twisted.conch.ssh import transport, userauth, connection
from twisted.conch.ssh import common, channel
from twisted.conch.ssh.keys import Key
from twisted.internet import defer, reactor, protocol

import struct

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

    def __init__(self, command, result, *args, **kwargs):
        """
        @param command: command to run
        @type command: string
        @param result: deferred to callback (exit, stdout, stderr)
                       or errback (code, value) with
        @type result: Deferred
        @param conn: connection to create the channel on
        @type conn: Twisted connection object
        """
        channel.SSHChannel.__init__(self, *args, **kwargs)
        self.command = command
        self.result = result
        self.out = ''
        self.err = ''
        self.exit = 1

    def openFailed(self, reason):
        if isinstance(reason, ConchError):
            res  = (reason.data, reason.value)
        else:
            res = (reason.code, reason.desc)

        result.errback(res)
        channel.SSHChannel.openFailed(self, reason)

    def channelOpen(self, _):
        req = self.conn.sendRequest(self, "exec", common.NS(self.command),
                                    wantReply=True)
        req.addCallback(lambda _: self.conn.sendEOF(self))

    def dataReceived(self, data):
        self.out = self.out + data

    def extReceived(self, dataType, data):
        if dataType == 1:
            self.err = self.err + data

    def request_exit_status(self, data):
        self.exit = struct.unpack('>L', data)[0]

    def eofReceived(self):
        if self.result is not None:
            self.result.callback((self.exit, self.out, self.err))

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

def sendCommand(connection, command, result=None):
    def done(result, executed):
        executed.callback(connection)
        return result

    executed = defer.Deferred()
    result.addCallback(done, executed)
    channel = CommandChannel(command, result, conn=connection)
    connection.openChannel(channel)
    return executed

def disconnect(connection):
    connection.transport.loseConnection()


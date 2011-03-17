from twisted.conch.ssh import transport, userauth, connection
from twisted.conch.ssh import common, channel
from twisted.conch.ssh.keys import Key
from twisted.internet import defer, reactor

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

    def extReceived(self, data):
        self.err = self.err + data

    def eofReceived(self):
        if self.deferStdOut is not None:
            self.deferStdOut.callback(self.out)
        if self.deferStdErr is not None:
            self.deferStdErr.callback(self.err)

def connect(host, username, password, port=22):
    pass

        

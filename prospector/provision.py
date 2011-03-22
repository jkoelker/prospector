from twisted.internet import defer
from twisted.python import log

from prospector import settings, ssh

def runCmd(connection, cmd):
    result = defer.Deferred()
    connection.addCallback(ssh.sendCommand, cmd, result)
    return result

def bootstrap(connection):
    def success(result):
        ex, out, err = result
        if ex != 0:
            log.msg("ERROR:\n\texit: %s\n\tout: %s \n\terr: %s" % (ex,
                                                                   out,
                                                                   err))
            return False

        return True

    def error(result):
        return False
    
    user = settings.config["web"]["user"]
    sesame = settings.config["web"]["sesame"]

    baseUrl = "%s://%s:%s@%s:%s/config" % (user,
                                           sesame,
                                           settings.getHost(),
                                           settings.getPort())

    cmd = "wget -O /tmp/bootstrap.sh %s/bootstrap.sh && " % baseUrl + \
          "sh /tmp/bootstrap.sh %s" % baseUrl

    result = runCmd(connection, cmd)
    result.addCallbacks(success, error)
    return result

def provision(host, username, password, port=22):
    connection = ssh.connect(host, username, password, port)
    result = bootstrap(connection)
    connection.addCallback(ssh.disconnect)
    return result


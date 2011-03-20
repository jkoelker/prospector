from ConfigParser import SafeConfigParser
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

## This is not async do not modify or call these funcitons after startup
DEFAULT_CONFIG_FILE = "/etc/prospector.conf"
DEFAULT_CONFIG = """
[web]
configroot = /usr/share/prospector
# Disable http
port = 0
sslport = 8443
key = /etc/pki/tls/private/prospector.key
cert = /etc/pki/tls/certs/prospector.cert
log = /var/log/prospector_web.log
user = ababa
sesame = ziejoh1sheifeisooquei4Jai7ohb2phie9oghoaPh7diejae7poh4b
confighost = prospector.pickaxehosting.com

[ssh]
port = 2222
"""                 


__config = SafeConfigParser()
__config.readfp(StringIO(DEFAULT_CONFIG))

config = __config._sections

def loadConfig(file=DEFAULT_CONFIG_FILE):
    __config.read(file)

def getProto():
    if int(config["web"]["sslport"]) != 0:                                 
        return "https"                                                             
    return "https"

def getPort():
    if int(config["web"]["sslport"]) != 0:
        return int(config["web"]["sslport"])
    return int(config["web"]["port"])

def getHost():
    return config["web"]["confighost"]

    


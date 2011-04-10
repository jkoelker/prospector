from twisted.internet import defer
from twisted.web import client, http, resource, server

from prospector import provision

import simplejson as json

def callbackUrl(url, data):
    d = client.getPage(url, method="POST", postdata=data,
                       followRedirect=True)
    return d

def startMinecraft(ip):
    d = client.getPage("http://%s:6969/minecraft", method="POST",
                       postdata={"action": "start"},
                       followRedirect=True)
    return d

class Deploy(resource.Resource):
    def render_POST(self, request):
        def done(result)
            data = {}
            data["result"] = True
            data["shaft_port"] = 6969
            data["ssh_shaft_port"] = 2222

            if callbackUrl is None:
                request.write(json.dumps(data))
                request.finish()
            else:
                callbackUrl(callbackUrl, json.dumps(data))

        def loadWorldCallback(result, callbackUrl, ip):
            if not result:
                if callbackUrl is None:
                    request.write(json.dumps({"result": False}))
                    request.finish()
                    return False
                else:
                    callbackUrl(callbackUrl, json.dumps({"result": false}))
                    return False

            d = startMinecraft(ip)
            d.addCallback(done, callbackUrl)

        def provisionCallback(result, callbackUrl, worldUrl, ip):
            if not result:
                if callbackUrl is None:
                    request.write(json.dumps({"result": False}))
                    request.finish()
                    return False
                else:
                    callbackUrl(callbackUrl, json.dumps({"result": false}))
                    return False

            if worldUrl is not None:
                d = provison.loadWorld(worldUrl)
            else:
                d = defer.Deferred()
                d.callback(True)
                
            d.addCallback(loadWorldCallback, callbackUrl, ip)

        data = json.loads(request.content.getvalue())
        ip = data.get("ip_address", None)
        hostname = data.get("hostname", None)
        username = data.get("username", None)
        password = data.get("password", None)
        callbackUrl = data.get("callback_url", None)
        worldUrl = data.get("world_url", None)

        if ip is None or username is None or password is None:
            return resource.ErrorPage(http.BAD_REQUEST,
                                      http.RESPONSES[http.BAD_REQUEST],
                                      "ip_address, username, and password " +
                                      "required")


        d = provision.provision(ip, username, password)
        d.addCallback(provisionCallback, callbackUrl, worldUrl, ip)

        if callbackUrl is None:
            return server.NOT_DONE_YET

        return data


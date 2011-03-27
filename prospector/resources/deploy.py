from twisted.web import client, resource, server

from prospector import provision

import simplejson as json

def callbackUrl(url, data):
    d = client.getPage(url, method="POST", postdata=data,
                       followRedirect=True)
    return d

def fail(data):
    data["result"] = False
    callbackUrl(data["callback_url"], json.dumps(data))

class Deploy(resource.Resource):
    def render_POST(self, request):
        def loadWorldCallback(result, data):
            if not result:
                fail(data)
                return False

            data["result"] = True
            data["shaft_port"] = 6969
            data["ssh_shaft_port"] = 2222

            callbackUrl(data["callback_url"], json.dumps(data))

        def provisionCallback(result, data):
            if not result:
                fail(data)
                return False

            d = provison.loadWorld(data["world_url"])
            d.addCallback(loadWorldCallback, data)

        data = request.content.getvalue()
        ip = data["ip_address"]
        hostname = data["hostname"]
        username = data["username"]
        password = data["password"]
        callbackUrl = data["callback_url"]
        worldUrl = data["world_url"]

        d = provision.provision(ip, username, password)
        d.addCallback(provisionCallback, data)
        return data


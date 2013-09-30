import sys
from boto import exception as cloudexception
from vpynup.provider import Provider


class VpnBootstrap(object):

    def __init__(self, json_config=None):
        try:
            if(json_config is not None and 'provider' in json_config):
                self.provider = Provider(**json_config['provider'])
        except cloudexception.NoAuthHandlerFound as e:
            sys.stderr.write("Failed to connect to cloud provider: "
                             "{0}\n".format(e.message))
            sys.exit(400)

    def start(self):
        self.provider.provision()

    def stop(self):
        pass

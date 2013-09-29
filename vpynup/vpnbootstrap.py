import sys
from boto import ec2, exception
from vpynup.provider import Provider

class VpnBootstrap(object):


    def __init__(self, json_config=None):
        try:
           if(json_config is not None and
              'provider' in json_config and
              'parameters' in json_config['provider']):
               self.provider = Provider(**json_config['provider']['parameters'])
               pass
        except exception.NoAuthHandlerFound as e:
           sys.stderr.write("Failed to connect to cloud provider: "
                            "{0}\n".format(e.message))
           sys.exit(400)

    def start(self):
        self.provider.provision()

    def stop(self):
        pass

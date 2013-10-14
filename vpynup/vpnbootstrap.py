import sys
from boto import exception as cloudexception
from fabric.api import execute as fabric_run
from vpynup.provider import Provider
from vpynup.fabricant import Fabricant


class VpnBootstrap(object):

    def __init__(self, json_config=None):
        try:
            if(json_config is not None and 'provider' in json_config):
               self.provider = Provider(**json_config['provider'])

            if(json_config is not None and 'provider' in json_config and
               'instance' in json_config['provider']):
                self.key_filename = json_config['provider']['instance']['key_path']
        except cloudexception.NoAuthHandlerFound as e:
            sys.stderr.write("Failed to connect to cloud provider: "
                             "{0}\n".format(e.message))
            sys.exit(400)

    def start(self):
        prov = self.provider.provision()
        print(self.provider.get_hostname())
        print(self.key_filename)
        self.fabricant = Fabricant(host=self.provider.get_hostname(), key_filename=self.key_filename)
        fabric_run(self.fabricant())

    def stop(self):
        self.provider.unprovision()

import sys
import time
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
       
        _istatus = 'pending'
        while(_istatus != 'running'):
            _istatus = self.provider.instance.state
            sys.stdout.write("Wait until instance is running. Status is: {0}".format(_istatus))
            time.sleep(5)
        self.fabricant = Fabricant(host=self.provider.get_hostname(), key_filename=self.key_filename)
        fabric_run(self.fabricant)

    def stop(self):
        self.provider.unprovision()

#!/usr/bin/env python
import sys
import os
import time
import json
from fabric.api import execute as fabric_run
from vpynup import provider
from vpynup import fabricant


class StarGate(object):
    def __init__(self, config_file=None):
        self.auth_params = None
        self.instance_params = None
        self.instance = None

        self.conn = None

        self._load_config(config_file)
        self.conn = provider.cloud_connect(self.auth_params)

        if self.conn is None:
            raise Exception("Connection to cloud provider failed")

    def _load_config(self, config_path=None):
        rval = False
        if config_path:
            try:
                with open(config_file) as jsonfd:
                    dict_config = json.load(jsonfd)
            except Exception as e:
                sys.stderr.write("json config loading failed:"
                                 " {0}\n".format(e.message))
        else:
            sys.stderr.write("No config file provided or the file "
                             "could not be found\n")

        if self.__validate_config(dict_config):
            self.auth_params = dict_config['provider']['auth']
            self.instance_params = dict_config['provider']['instance']
            rval = True
        else:
            sys.stderr.write("Json config is not valid: some attributes "
                             "are missing. Please check vpin documentation\n")

        return rval

    def __validate_config(self, dict_config):
        rval = True

        if(dict_config and 'provider' in dict_config and
           'auth' in dict_config['provider']):
            self.auth_params = dict_config['provider']['auth']
        else:
            rval = False

        if(dict_config and 'provider' in dict_config and
           'instance' in dict_config['provider']):
            self.instance_params = dict_config['provider']['instance']
        else:
            rval = False
        return rval

    def init(self):
        rval = True
        _cwd = os.getcwd()

        _sdict = ({"provider": {
                       "name": "aws",
                       "auth": {
                           "aws_access_key_id": "",
                           "aws_secret_access_key": ""
                       },
                       "instance": {
                           "image_id": "ami-c30360aa",
                           "key_name": "",
                           "key_path": ""
                       }
                     }
                  })

        _aws_access_key_id = raw_input('enter/copy your amazon access key id: ')
        _aws_secret_access_key = raw_input('enter/copy your amazon secret access id: ')
        _aws_sshkey_name = raw_input('enter the name of your amazon ssh key: ')
        _aws_sshkey_path = raw_input('enter the path to the corresponding private key (.pem file): ')

        if '' not in [ _aws_access_key_id, _aws_secret_access_key, _aws_sshkey_name, _aws_sshkey_path ]:
            _sdict['provider']['auth']['aws_access_key_id'] = _aws_access_key_id
            _sdict['provider']['auth']['aws_secret_access_key'] = _aws_secret_access_key
            _sdict['provider']['instance']['key_name'] = _aws_sshkey_name
            _sdict['provider']['instance']['key_path'] = _aws_sshkey_path

            try:
                with open("{0}/{1}".format(cwd), "default.json") as jfd:
                    json.dump(_sdict, jfd, indent=4)
            except IOError as e:
                sys.stderr.write("File creation failed: {0}".format(e.message))
                rval = False
        else:
            sys.stderr.write("Not all required parameters have been provided.\n")
            rval = False
        return rval

    def up(self):
        _r = self.start()
        if _r is not None:
            print self.gate_hostname()
            self.provision()

        return _r

    def start(self, wait=True):
        _instance = provider.start_instance(self.conn, self.instance_params)
       
        if _instance is not None:
            _istatus = 'pending'
            while(_istatus != 'running'):
                _istatus = self.gate_status()
                sys.stdout.write("Wait until instance is running. Status is: {0}\n".format(_istatus))
                time.sleep(5)
            self.instance = _instance
        return _instance


    def provision(self):
        fabric_run(fabricant.provision(self.gate_hostname(), self.instance_params['key_path']))

    def stop(self):
        provider.terminate_instance(self.conn, self.instance.id)

    def gate_status(self):
        rval = 'halted'
        if self.instance:
            self.instance.update()
            rval = self.instance.status
        return rval

    def gate_hostname(self):
        self.instance.update()
        return self.instance.public_dns_name

    def save(self):
        raise NotImplementedError

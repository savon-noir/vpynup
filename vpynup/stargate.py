#!/usr/bin/env python
import sys
import os
import time
import json
from fabric.api import execute as fabric_run
from vpynup import provider
from vpynup import fabricant


def _default_config_path():
    _cwd = os.getcwd()
    _config_file = "{0}/{1}".format(_cwd, "vpinup.json")
    return _config_file


def _load_config(config_path=None):
    dict_config = None

    if config_path is None:
        _config_file = _default_config_path()
    else:
        _config_file = config_path

    if not os.path.exists(_config_file):
        sys.stderr.write("config file {0} does not exists. Run vpinup init.\n")
        sys.exit(1)

    try:
        with open(_config_file) as jsonfd:
           dict_config = json.load(jsonfd)
    except Exception as e:
        sys.stderr.write("json config loading failed: {0}\n".format(e.message))
        sys.exit(1)

    if not __validate_config(dict_config):
        sys.stderr.write("Json config is not valid: some attributes "
                         "are missing. Please check vpin documentation\n")
        sys.exit(1)

    return dict_config


def __validate_config(dict_config):
    rval = False

    if(dict_config and 'provider' in dict_config and
       'auth' in dict_config['provider'] and
       'instance' in dict_config['provider']):
        rval = True

    return rval


def init():
    rval = True

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

    _aws_provider = raw_input('enter your provider: aws/euca [aws] ')
    _aws_provider = _aws_provider or "aws"
    _aws_access_key_id = raw_input('enter/copy your amazon access key id: ')
    _aws_secret_access_key = raw_input('enter/copy your amazon secret access id: ')
    _aws_sshkey_name = raw_input('enter the name of your amazon ssh key: ')
    _aws_sshkey_path = raw_input('enter the path to the corresponding private key (.pem file): ')
    _aws_sshuser = raw_input('enter the name of your ssh user: []')

    if '' not in [_aws_access_key_id, _aws_secret_access_key, _aws_sshkey_name, _aws_sshkey_path]:
        _sdict['provider']['auth']['aws_access_key_id'] = _aws_access_key_id
        _sdict['provider']['auth']['aws_secret_access_key'] = _aws_secret_access_key
        _sdict['provider']['instance']['key_name'] = _aws_sshkey_name
        _sdict['provider']['instance']['key_path'] = _aws_sshkey_path
   
    if _aws_provider == "euca":
        _sdict['provider']['name'] = _aws_provider
        _sdict['provider']['auth']['port'] = 8773
        _sdict['provider']['auth']['path'] = "/services/Eucalyptus"
        _sdict['provider']['auth']['is_secure'] = False
        _sdict['provider']['auth']['region']={}
        _sdict['provider']['auth']['region']['name'] = "eucalyptus"
        _sdict['provider']['auth']['region']['endpoint'] ="eucalyptus.ecc.eucalyptus.com"
        _sdict['provider']['instance']['user'] = _aws_sshuser or "ec2-user"
        _sdict['provider']['instance']['image_id'] = "emi-8B443944"

        try:
            _fname = _default_config_path()
            with open(_fname, 'w') as jfd:
                json.dump(_sdict, jfd, indent=4)
        except IOError as e:
            sys.stderr.write("File {0} creation failed: {1}".format(_fname, e.strerror))
            rval = False
    else:
        sys.stderr.write("Not all required parameters have been provided.\n")
        rval = False
    return rval


def up():
    rval = start()
    _provisioned = not_provisioned()
    if rval:
        if not _provisioned:
            rval = provision()
        else:
            sys.stdout.write("Remote host already provisioned. run provision to force\n")

        if not rval:
            sys.stderr.write("Failed to provision the vm on the provider\n")
    else:
        sys.stderr.write("Failed to stage the vm on the provider\n")

    return rval


def start(wait=True):
    rval = False
    _instance = None
    _instance_id = None

    _config_dict = _load_config()
    _auth_params = _config_dict['provider']['auth']
    _instance_params = _config_dict['provider']['instance']

    if 'instance_id' in _config_dict['provider']['instance']:
        _instance_id = _config_dict['provider']['instance']['instance_id']

    conn = provider.cloud_connect(**_auth_params)

    if conn is not None and _instance_id is None:
        _instance = provider.create_instance(conn, _instance_params)
    elif conn is not None and _instance_id is not None:
        _instance = provider.start_instance(conn, _instance_id)

    if _instance is not None:
        _istatus = 'pending'
        while(_istatus != 'running' and wait):
            _istatus = status(_instance)
            sys.stdout.write("Wait until instance is running. Status is: {0}\n".format(_istatus))
            time.sleep(5)
        rval = True
        save(_instance)

    return rval


def provision():
    _config_dict = _load_config()
    _instance_params = _config_dict['provider']['instance']

    _hostname = gate_hostname()
    _i = 0
    while(_i < 10 and _hostname == ''):
        _hostname = gate_hostname()
        _i = _i + 1
        time.sleep(5)
    _sshkeys = _instance_params['key_path']
    if 'user' not in _instance_params:
        _user = 'ubuntu'
    else:
        _user = _instance_params['user']
    time.sleep(5)
    retdict = fabric_run(fabricant.provision, _hostname, _user, _sshkeys)

    if True in retdict.values():
        save(None, True)
        rval = True
    else:
        rval = False

    return rval


def terminate():
    rval = False
    _config_dict = _load_config(_default_config_path())
    _auth_params = _config_dict['provider']['auth']

    _instance = get_instance()
    conn = provider.cloud_connect(**_auth_params)
    if conn is None:
        conn = provider.cloud_connect(**_auth_params)
    if conn and _instance is not None:
        rval = provider.terminate_instance(conn, _instance.id)
        sys.stdout.write("instance destroyed successfully\n")
    return rval

def stop():
    rval = False
    _config_dict = _load_config(_default_config_path())
    _auth_params = _config_dict['provider']['auth']

    _instance = get_instance()
    conn = provider.cloud_connect(**_auth_params)
    if conn is None:
        conn = provider.cloud_connect(**_auth_params)
    if conn and _instance is not None:
        rval = provider.stop_instance(conn, _instance.id)
        sys.stdout.write("instance halted successfully\n")
    return rval

def reboot():
    sys.stderr.write("not yet :p\n")


def get_instance(instance_id=None):
    instance = None
    _instance_id = instance_id
    _config_dict = _load_config(_default_config_path())
    _auth_params = _config_dict['provider']['auth']

    if _instance_id is None and 'instance_id' in _config_dict['provider']['instance']:
        _instance_id = _config_dict['provider']['instance']['instance_id']

    conn = provider.cloud_connect(**_auth_params)
    _reservations = conn.get_all_instances(instance_ids=[_instance_id])

    if _reservations is not None and len(_reservations[0].instances):
        _instance = _reservations[0].instances.pop()
    return _instance


def status(instance=None):
    rval = 'unknown'
    _instance = instance

    if _instance:
        _instance.update()
    else:
        _config_dict = _load_config(_default_config_path())
        if 'instance_id' in _config_dict['provider']['instance']:
            _instance = get_instance(_config_dict['provider']['instance']['instance_id'])
        else:
            rval = 'not started'

    if _instance is not None:
        rval = _instance.state
        save(_instance)

    return rval


def gate_hostname(instance=None):
    rval = None
    _instance = instance

    if _instance:
        _instance.update()
    else:
        _config_dict = _load_config(_default_config_path())
        if 'instance_id' in _config_dict['provider']['instance']:
            _instance = get_instance(_config_dict['provider']['instance']['instance_id'])
        else:
            rval = ''

    if _instance is not None:
        rval = _instance.public_dns_name
        save(_instance)

    return rval


def save(instance=None, provisioned=None):
    jdict = _load_config()

    if instance is not None and jdict:
        jdict['provider']['instance']['instance_id'] = instance.id
        jdict['provider']['instance']['instance_status'] = instance.state

        with open(_default_config_path(), "w") as jfd:
            json.dump(jdict, jfd, indent=4)
    elif jdict and provisioned is not None:
        jdict['provider']['instance']['provisioned'] = str(provisioned)
        with open(_default_config_path(), "w") as jfd:
            json.dump(jdict, jfd, indent=4)
    else:
        sys.stderr.write("Session could not be save\n")

def not_provisioned():
    rval = False

    jdict = _load_config()
    if jdict and 'provisioned' in jdict['provider']['instance']:
        rval = bool(jdict['provider']['instance']['provisioned'])
    return rval

import sys
import os
from fabric.tasks import Task
from fabric.api import env
from fabric.operations import run, put, sudo, get
from fabric.contrib import files as fabfiles


class Fabricant(Task):
    def __init__(self, host=None, key_filename=None):
        self.host = host
        if not os.path.exists(key_filename):
            raise Exception("SSH key path does not exists: {0}".format(key_filename))
        else:
            self.key_filename = key_filename

        env.hosts = [ self.host ]
        env.user = 'ubuntu'
        env.key_filename = [ self.key_filename ]

    def get_distro(self):
        d_val = None
        if fabfiles.exists('/etc/debian_version'):
            d_val = "Debian"
        elif fabfiles.exists('/etc/fedora-release'):
            d_val = "Fedora"
        elif fabfiles.exists('/etc/arch-release'):
            d_val = "Archlinux"
        elif fabfiles.exists('/etc/redhat-release'):
            d_val = "RedHat"
        else:
            d_val = "Unsupported"
        return d_val

    def remote_dir_copy(self, source_dir, print_output=True):
        _dpath = None
        _rout = run("mktemp -d")
    
        if _rout.failed and print_output:
            sys.stderr.write("Failed to create remote tmp directory") 
        elif not os.path.exists(source_dir):
            sys.stderr.write("Source directory {0} does not exists".format(source_dir))
        else:
            _dpath = _rout.stdout
            put(source_dir, _dpath)
        return _dpath

    def stage_puppet(self, puppet_dir, manifest_file="init.pp", print_output=True):
        _distro = self.get_distro()
        if _distro == "Debian":
            sudo("apt-get -y update")
            sudo("apt-get -y install puppet")
            sudo("puppet apply --modulepath={0}/puppet/modules/ {0}/puppet/manifests/{1}".format(puppet_dir, manifest_file))
        elif print_output:
            sys.stderr.write("Distro {0} is not yet supported".format(_distro))
        
    def remote_config_get(self, remote_file, local_file, print_output=True):
        _rsize = 0
        _fpath = None
        _rout = sudo("mktemp XXXXXXXX.tgz")
        _fout = sudo("cat {0}".format(remote_file), quiet=True)
        if ((_rout.failed or _fout.failed) and print_output):
            sys.stderr.write("Failed to create temp file for remote copy")
        else:
            _fpath = _rout.stdout
            _rdata = _fout.stdout
            fabfiles.append(path=_fpath, text=_rdata, use_sude=True)
            get(_fpath, local_file)
            sudo('rm -rf {0}'.format(_fpath))
            _rsize = len(_rdata)
        return _rsize

    def run(self):
        _mods_dir = "/vagrant/puppet/"
        _puppet_conf_dir = self.remote_dir_copy(_mods_dir)
        if _puppet_conf_dir is not None:
            self.stage_puppet(_puppet_conf_dir)
            r = self.remote_config_get("/etc/openvpn/ovpn/download-configs/clientlol.tgz", "/tmp/clientlol.tgz")
        else:
            sys.stderr.write("Could not push puppet configs on remote host")

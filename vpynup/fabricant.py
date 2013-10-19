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
        self.debug = False

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

    def remote_dir_copy(self, local_dir, remote_dir=None, print_output=True):
        _dpath = None

        if remote_dir is None:
            _rout = run("mktemp -d")
        else:
            _rout = run("mkdir -p {0}".format(remote_dir))
    
        if _rout.failed and print_output:
            sys.stderr.write("Failed to create remote directory\n") 
        elif not os.path.exists(local_dir):
            sys.stderr.write("Source directory {0} does not exists\n".format(local_dir))
        else:
            _dpath = _rout.stdout if remote_dir is None else remote_dir
            put(local_dir, _dpath)
        return _dpath

    def stage_puppet(self, puppet_dir, manifest_file="init.pp", print_output=True):
        _distro = self.get_distro()
        if _distro == "Debian":
            sudo("apt-get -y update")
            sudo("apt-get -y install puppet")
            sudo("puppet apply --modulepath={0}/puppet/modules/ {0}/puppet/manifests/{1}".format(puppet_dir, manifest_file))
        elif print_output:
            sys.stderr.write("Distro {0} is not yet supported\n".format(_distro))
        
    def remote_config_get(self, remote_file, local_file, print_output=True):
        _rsize = 0
        _fpath = None
        _fout = run("mktemp XXXXXXXX.tgz")
        _dout = sudo("cat {0}".format(remote_file), quiet=True)
        if ((_dout.failed or _fout.failed) and print_output):
            sys.stderr.write("Failed to create temp file for remote copy\n")
        else:
            _fpath = _fout.stdout
            _rdata = _dout.stdout
            fabfiles.append(path=_fpath, text=_rdata, use_sudo=True)
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
            sys.stderr.write("Could not push puppet configs on remote host\n")

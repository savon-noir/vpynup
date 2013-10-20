import sys
import os
from fabric.api import env, task
from fabric.operations import run, put, sudo, get
from fabric.contrib import files as fabfiles


@task
def get_distro():
    d_val = None
    if fabfiles.exists('/etc/debian_version'):
        d_val = "Debian"
    elif fabfiles.exists('/etc/fedora-release'):
        d_val = "Fedora"
    elif fabfiles.exists('/etc/arch-release'):
        d_val = "Arch Linux"
    elif fabfiles.exists('/etc/redhat-release'):
        d_val = "RedHat"
    else:
        d_val = "Unsupported"

    return d_val


@task
def remote_dir_copy(local_dir, remote_dir=None, print_output=True):
    _dpath = None

    if remote_dir is None:
        _rout = run("mktemp -d")
    else:
        _rout = run("mkdir -p {0}".format(remote_dir))

    if _rout.failed and print_output:
        sys.stderr.write("Failed to create remote directory\n")
    elif not os.path.exists(local_dir):
        sys.stderr.write("Source directory {0} does "
                         "not exists\n".format(local_dir))
    else:
        _dpath = _rout.stdout if remote_dir is None else remote_dir
        put(local_dir, _dpath)
    return _dpath


@task
def stage_puppet(puppet_dir, manifest_file="init.pp", print_output=True):
    _distro = get_distro()
    if _distro == "Debian":
        sudo("apt-get -y update")
        sudo("apt-get -y install puppet")
        sudo("puppet apply --modulepath={0}/puppet/modules/ "
             "{0}/puppet/manifests/{1}".format(puppet_dir, manifest_file))
    elif print_output:
        sys.stderr.write("Distro {0} is not yet supported\n".format(_distro))


@task
def remote_config_get(remote_file, local_file, print_output=True):
    rval = True
    _fpath = None
    _fout = run("mktemp /tmp/XXXXXXXX.tgz")
    if (_fout.failed and print_output):
        sys.stderr.write("Failed to create temp file for remote copy\n")
        rval = False
    else:
        _fpath = _fout.stdout
        _dout = sudo("cp {0} {1}".format(remote_file, _fpath))
        get(_fpath, local_file)
        sudo('rm -rf {0}'.format(_fpath))
    return rval


@task
def provision(target_ip, user='ubuntu', sshkey_path=None, target_port=22):
    r = True
    env['host_string'] = "{0}@{1}:{2}".format(user, target_ip, target_port)
    env['key_filename'] = sshkey_path

    _mods_dir = "/vagrant/puppet/"
    _puppet_conf_dir = remote_dir_copy(_mods_dir)
    if _puppet_conf_dir is not None:
        stage_puppet(_puppet_conf_dir)
        r = remote_config_get("/etc/openvpn/ovpn/download-configs/client1.tar.gz",
                              "/tmp/clientlol.tgz")
    else:
        sys.stderr.write("Could not push puppet configs on remote host\n")

    return r

import sys
import os
import uuid
import pkg_resources
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
def stage_puppet(print_output=True):
    rval = True
    _distro = get_distro()

    if _distro == "Debian":
        sudo("apt-get -y update")
        rcode = sudo("apt-get -y install puppet")

        if rcode.return_code != 0:
            sys.stderr.write("Failed to install puppet on target host")
            rval = False

    elif print_output:
        sys.stderr.write("Distro {0} is not yet supported\n".format(_distro))
        rval = False
    return rval


@task
def puppet_apply(puppet_dir, manifest_file="init.pp", print_output=True):
    rval = False
    _pdir = ''
    if fabfiles.exists("{0}/puppet/modules/".format(puppet_dir)):
        _pdir = "--modulepath={0}/puppet/modules/".format(puppet_dir)

    _pcmd = "puppet apply {0} {1}/puppet/manifests/{2}".format(_pdir,
                                                               puppet_dir,
                                                               manifest_file)
    rcode = sudo(_pcmd)
    if not rcode.failed:
        rval = True
    return rval


@task
def stage_puppet_modules(puppet_mods=[]):
    rval = True

    for pmod in puppet_mods:
        rcode = sudo("puppet module install --force {0}".format(pmod))
        if rcode.return_code != 0:
            sys.stderr.write("Failed to install puppet module {0}".format(pmod))
            rval = False
    return rval


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
        if _dout.return_code == 0:
            get(_fpath, local_file)
        else:
            sys.stderr.write("Failed to copy and get remote file\n")
        sudo('rm -rf {0}'.format(_fpath))
    return rval


@task
def provision(target_ip, user='ubuntu', sshkey_path=None, target_port=22):
    r = True
    modules_list = ['luxflux/openvpn',
                    'puppetlabs/firewall',
                    'thias/sysctl',
                    'puppetlabs/concat']

    env['host_string'] = "{0}@{1}:{2}".format(user, target_ip, target_port)
    env['key_filename'] = sshkey_path

    r = stage_puppet()

    if r is True:
        r = stage_puppet_modules(modules_list)
        if r is False:
            sys.stderr.write("Failed to install required puppet modules")
    else:
        sys.stderr.write("Failed to bootstrap puppet agent on remote host\n")
        r = False

    if r is True:
        _pcontext={"remote_host": target_ip}
        _mods_dir = pkg_resources.resource_filename("vpynup", "puppet")
        print "DEBUG " + _mods_dir
        _pmanifest = "init.pp"
        _src_file = "{0}/manifests/{1}".format(_mods_dir, _pmanifest)
        _dst_dir = "/tmp/{0}/".format(str(uuid.uuid4()))
        _dst_file = "{0}/puppet/manifests/{1}".format(_dst_dir, _pmanifest)
        ret = run("mkdir -p {0}/puppet/manifests/".format(_dst_dir))

        if ret.succeeded:
            fabfiles.upload_template(_src_file, _dst_file, context=_pcontext)
            r = puppet_apply(_dst_dir)
        else:
            r = False
        run("rm -rf {0}".format(_dst_dir))

    if r is False:
        sys.stderr.write("Failed to apply global pupet manifests\n")

    if get_new_config('default'):
        sys.stdout.write("Client configuration successfully downloaded\n")
    else:
        sys.stderr.write("Failed to create or get the client config\n")
    return r


@task
def get_new_config(client_name, outfile=None):
    r = False
    _rcpath = "/etc/openvpn/ovpn/download-configs/{0}.tar.gz".format(client_name)
    if outfile is None:
        _lcpath = "/tmp/{0}.tar.gz".format(client_name)
    else:
        _lcpath = outfile

    r = get(_rcpath, _lcpath)
    return r

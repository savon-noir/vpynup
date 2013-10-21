VPyN-UP
========

Use case
--------

Quick, I need an on demand VPN server. VPYNUP will enable you to quickly stage a remote VPN server on any IaaS provider (supported by boto).

Show0r me
---------

initialize your environment::

    $ mkdir mystargate
    $ cd mystargate
    $ vpyn init
    enter/copy your amazon access key id: my_amazon_access_key
    enter/copy your amazon secret access id: my_amazon_secret_key
    enter the name of your amazon ssh key: name_of_the_aws_ssh_key_to_login 
    enter the path to the corresponding private key (.pem file): /path/to/ssh/file
    $ ls
    vpinup.json

stage and provision your vm online::

    $ vpyn up
    Wait until instance is running. Status is: pending
    Wait until instance is running. Status is: pending
    <... lot of output ...>
    <... still in debug mode, kinda...>
    [ubuntu@some.hostname.amazonaws.com:22] sudo: cp /etc/openvpn/ovpn/download-configs/client1.tar.gz /tmp/pUtXtTtv.tgz
    [ubuntu@some.hostname.amazonaws.com:22] download: /tmp/clientlol.tgz <- /tmp/pUtXtTtv.tgz

force provisioning::

    $ vpyn provision
    <... lot of output ...>
    <... still in debug mode, kinda...>
    [ubuntu@some.hostname.amazonaws.com:22] sudo: cp /etc/openvpn/ovpn/download-configs/client1.tar.gz /tmp/pUtXtTtv.tgz
    [ubuntu@some.hostname.amazonaws.com:22] download: /tmp/clientlol.tgz <- /tmp/pUtXtTtv.tgz

stop your openvpn instance::

    $ vpyn halt
    instance successfully stopped

start it again::

    $ vpyn up
    $ vpyn status
    instance status: running
    $ vpyn hostname
    instance hostname: some.hostname.amazonaws.com


Under the hood
--------------

Following technologies are abused by vpnup:

- boto, to chat and argue with the provider
- fabric and fabtools, to stage a puppet client package
- puppet, to load up the different manifests written for the different supported VPN

For now, only OpenVPN is supported.

Dependencies
------------

- Boto
- fabric
- python dev headers, for compiling pycrypto

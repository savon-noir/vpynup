VPyN-UP
========

Use case
--------

Quick, I need an on demand VPN server. VPYNUP will enable you to quickly stage a remote VPN server on any IaaS provider (supported by boto).

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

from distutils.core import setup
from setuptools import setup, find_packages

with open("README.rst") as rfile:
    long_description = rfile.read()

setup(
    name='vpynup',
    version='0.1',
    author='Ronald Bister',
    author_email='mini.pelle@gmail.com',
    packages=['vpynup'],
    scripts = ["vpyn", ],
#    package_data = {
#                        'puppet': ['puppet/manifests/init.pp'],
#                    },
    data_files=[('vpynup/puppet', ['vpynup/puppet/manifests/init.pp']),],

    install_requires = ['boto'],
    url="http://pypi.python.org/pypi/vpynup/",
    license='Creative Common "Attribution" license (CC-BY) v3',
    description=('vpn lolz'),
    long_description=long_description,
    classifiers=["Development Status :: 5 - Production/Stable",
                 "Environment :: Console",
                 "Programming Language :: Python :: 2.6",
                 "Programming Language :: Python :: 2.7",
                 "Topic :: System :: Networking"]
)

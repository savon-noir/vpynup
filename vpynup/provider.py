import sys
from boto import ec2 as cloudapi
from boto import exception as cloudexception


class Provider(object):

    def __init__(self, **kwargs):
        self.connection = None
        self.image_id = None
        self.key_name = None
        self.instance_id = None
        self.instance = None

        try:
            if 'auth' in kwargs:
                self.connection = cloudapi.connection.EC2Connection(**kwargs['auth'])
            elif 'aws_access_key_id' in kwargs and 'aws_secret_access_key':
                self.connection = cloudapi.connection.EC2Connection(**kwargs)
            else:
                raise Exception("Failed to connect to cloud provider: check credentials")
        except:
            raise

        if('instance' in kwargs and 'image_id' in kwargs):
            self.image_id = kwargs['instance']['image_id']
        else:
            self.image_id = 'ami-c30360aa'

        if('instance' in kwargs and 'key_name' in kwargs['instance']):
            keypair_name = kwargs['instance']['key_name']
            self.key_name = self.get_keypair(keypair_name)
        else:
            raise Exception("Key pair auto creation not supported: please "
                            "provide an existing key pair name in json file")

    def get_image(self, image_id):
        _cloud_img = None
        try:
            _cloud_img = self.connection.get_image(image_id)
        except cloudexception.EC2ResponseError as e:
            e_msg = "get image failed: {0} ({1})\n".format(e.message, e.code)
            sys.stderr.write(e_msg)
            sys.exit(e.code)

        return _cloud_img

    def get_keypair(self, key_name):
        _key_pair = None
        _key_pair = self.connection.get_key_pair(key_name)

        return _key_pair

    def get_instance(self, instance_id):
        _instance = None
        _reservations = self.connection.get_all_instances(instance_ids=[instance_id])
        if _reservations is not None and len(_reservations[0].instances):
            _instance = _reservations[0].instances.pop()
        return _instance

    def get_hostname(self):
        return self.instance.public_dns_name if self.instance is not None else ''

    def get_instance_status(self, instance_id):
        _instance = self.get_instance(instance_id)
        return _instance.state if _instance is not None else None

    def provision(self):
        _reservations = None
        if(self.connection is not None and
            self.image_id is not None and
            self.key_name is not None):
            _reservations = self.connection.run_instances(image_id=self.image_id,
                                                          key_name=self.key_name.name,
                                                          instance_type='t1.micro')
        if(_reservations and (len(_reservations.instances) == 1)):
            self.instance = _reservations.instances.pop()
            self.instance_id = self.instance.id
        else:
            sys.stderr.write("Some parameters are not correctly set, "
                             "please check your json config file or "
                             "instance could not be started")
        return _reservations

    def unprovision(self):
        if(self.get_instance(self.instance_id) is not None):
            _reservations =self.connection.terminate_instances(instance_ids=[self.instance_id])
        else:
            sys.stderr.write("Instance for VPN does not exists. "
                             "Please manually check if it is still running")
        return _reservations

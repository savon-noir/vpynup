import sys
from boto import ec2 as cloudapi
from boto import exception as cloudexception


class Provider(object):

    def __init__(self, **kwargs):
        self.connection = None
        self.image = None
        self.key_name = None

        try:
            if 'auth' in kwargs:
                self.connection = cloudapi.connection.EC2Connection(**kwargs['auth'])
            else:
                print "raise exception"
        except:
            raise

        if('instance' in kwargs and 'image_id' in kwargs):
            image_id = kwargs['instance']['image_id']
            self.image = self.__get_image(image_id)
        else:
            self.image = self.__get_image()

        if('instance' in kwargs and 'key_name' in kwargs['instance']):
            keypair_name = kwargs['instance']['key_name']
            self.key_name = self.__get_keypair(keypair_name)
        else:
            sys.stderr.write("Key pair auto creation not supported: please "
                             "provide an existing key pair name in json file")

    def __get_image(self, image_id='ami-c30360aa'):
        _cloud_img = None
        try:
            _cloud_img = self.connection.get_image(image_id)
        except cloudexception.EC2ResponseError as e:
            e_msg = "get image failed: {0} ({1})\n".format(e.message, e.code)
            sys.stderr.write(e_msg)
            sys.exit(e.code)

        return _cloud_img

    def __get_keypair(self, keypair):
        _key_pair = None
        _key_pair = self.connection.get_key_pair(keypair)

        return _key_pair

    def provision(self):
        print self.connection
        print self.image
        print self.key_name
        if(self.connection is not None and
           self.image is not None and
           self.key_name is not None):
            self.connection.run_instances(image_id=self.image.id,
                                          key_name=self.key_name.name,
                                          instance_type='t1.micro')
        else:
            sys.stderr.write("Some parameters are not correctly set, "
                             "please check your json config file")

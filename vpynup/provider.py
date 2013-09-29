from boto import ec2, exception
import sys


class Provider(object):

    def __init__(self, provider="aws", **kwargs):
        try:
            self.connection = ec2.connection.EC2Connection(**kwargs)
        except:
            raise

    def provision(self, image_id='ami-c30360aa'):
        try:
            self.image = self.connection.get_image(image_id)
        except exception.EC2ResponseError as e:
            sys.stderr.write("get image failed: {0} ({1})\n".format(e.message, e.code))
            sys.exit(e.code)

import sys
from boto import ec2 as cloudapi
from boto import exception as cloudexception


def provider_connect(**kwargs):
    conn = None

    try:
        if 'aws_access_key_id' in kwargs and 'aws_secret_access_key':
            conn = cloudapi.connection.EC2Connection(**kwargs)
        else:
            sys.stderr.write("Failed to connect to cloud provider: "
                             "check credentials\n")
    except cloudexception.NoAuthHandlerFound as e:
        sys.stderr.write("Failed to connect to cloud provider: "
                         "{0}\n".format(e.message))

    return conn


def start_instance(conn, instance_params):
    _instance = None
    _image_id = instance_params['image_id']
    _key_name = instance_params['key_name']

    _reservations = conn.run_instances(image_id=_image_id,
                                       key_name=_key_name,
                                       instance_type='t1.micro')

    if(_reservations and (len(_reservations.instances) == 1)):
        _instance = _reservations.instances.pop()
    else:
        sys.stderr.write("Some parameters are not correctly set, "
                         "please check your json config file or "
                         "instance could not be started\n")
    return _instance


def terminate_instance(conn, instance_id):
    _instance = None
    _reservations = conn.terminate_instances(instance_ids=[instance_id])

    if(_reservations and (len(_reservations.instances) == 1)):
        _instance = _reservations.instances.pop()
    else:
        sys.stderr.write("Stopping the instance failed: "
                         "check your aws management console\n")
    return _instance

"""
This script deletes the ec2 instance, keypair association and security group
"""
import os
from time import sleep
import pprint
import boto3




instance_id = os.environ["EC2_ID"]

def terminate_instance(ec2_instance_id):
    """

    Function terminates the instance using the EC2_ID variable exported
    from ec2-create.py.
    To-do:
        add boto3auth for standardization

    """
    ec2_client = boto3.client("ec2", region_name="us-east-1")
    response = ec2_client.terminate_instances(InstanceIds=[ec2_instance_id])
    pprint.pp(response)


def delete_key_pair():
    """
     Function deletes the key pair from ec2-create.py.
    To-do:
        automate deletion of ssh key - risky

    """
    ec2_client = boto3.client("ec2", region_name="us-east-1")
    response = ec2_client.delete_key_pair(
        KeyName='ec2-demo'
    )
    pprint.pp(response)


def delete_security_group():
    """
    Function deletes the security group from ec2-create.py
    """
    ec2_client = boto3.client("ec2", region_name="us-east-1")
    response = ec2_client.delete_security_group(
        GroupName='EC2_DEMO'
    )
    pprint.pp(response)


print(terminate_instance.__doc__)
terminate_instance(instance_id)

print(delete_key_pair.__doc__)
delete_key_pair()

sleep(60)

print(delete_security_group.__doc__)
delete_security_group()

import boto3
import os
from time import sleep

instance_id = os.environ["EC2_ID"]
def terminate_instance(instance_id):
    ec2_client = boto3.client("ec2", region_name="us-east-1")
    response = ec2_client.terminate_instances(InstanceIds=[instance_id])
    print(response)

terminate_instance(instance_id)

def delete_key_pair():
    ec2_client = boto3.client("ec2", region_name="us-east-1")
    response = ec2_client.delete_key_pair(
        KeyName='ec2-demo'
    )
    print(response)

delete_key_pair()

sleep(60)

def delete_security_group():
    ec2_client = boto3.client("ec2", region_name="us-east-1")
    response = ec2_client.delete_security_group(
        GroupName='EC2_DEMO'
    )
    print(response)

delete_security_group()
import boto3
import os

INSTANCE_ID = os.getenv('EC2ID')

def terminate_instance(instance_id):
    ec2_client = boto3.client("ec2", region_name="us-west-2")
    response = ec2_client.terminate_instances(InstanceIds=[instance_id])
    print(response)

terminate_instance(INSTANCE_ID)
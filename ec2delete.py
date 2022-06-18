import boto3
import os

instance_id = os.environ["EC2_ID"]

def terminate_instance(instance_id):
    ec2_client = boto3.client("ec2", region_name="us-east-1")
    response = ec2_client.terminate_instances(InstanceIds=[instance_id])
    print(response)

terminate_instance(instance_id)

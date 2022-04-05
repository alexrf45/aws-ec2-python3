#!/usr/bin/env python3


AWS_REGION = "us-east-1"
EC2_RESOURCE = boto3.resource('ec2', region_name=AWS_REGION)
KEY_PAIR_NAME = 'aws-ec2'
AMI_ID = 'ami-07d02ee1eeb0c996c'


import boto3

def create_instance():
    instances = EC2_RESOURCE.create_instances(
        MinCount=1,
        MaxCount=1,
        ImageId=AMI_ID,
        InstanceType="t3.micro",
        KeyName=KEY_PAIR_NAME
    )

    print(instances["Instances"][0]["InstanceId"])
    

create_instance()



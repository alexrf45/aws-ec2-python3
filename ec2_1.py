#!/usr/bin/env python3

import boto3
from botocore.exceptions import ClientError
from time import sleep #allows script execution to pause as AWS CLI execution on AWS servers are not always instant. 
import os
import subprocess

REGION = 'us-east-1'
AMI_IMAGE_ID = 'ami-07d02ee1eeb0c996c'
INSTANCE_TYPE = 't2.micro'
DISK_SIZE_GB = 20
DEVICE_NAME = '/dev/xvda'
NAME = 'ec2-demo' #tag
OWNER = 'ec2demouser' #tag
RUNID = 'ec2-1' #tag
PUBLIC_IP = None
KEY_PAIR_NAME= 'ec2-demo'
USERDATA_SCRIPT = '''
#!/bin/bash
sudo apt-get update && sudo apt-get install -y wget git python3 nginx certbot
# Install Docker on ec2 instance:
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
sudo usermod -aG docker $USER
'''
min_count = 1 #Minimum number of ec2 instances created
max_count = 1 #Maximum number of ec2 instances created


## This function creates a keypair and saves it in the current directory as a .pem file
def create_key_pair():
    ec2_client = boto3.resource("ec2", region_name="us-east-1")
    outfile = open('ec2demo.pem', 'w')
    key_pair = ec2_client.create_key_pair(
        KeyName='ec2-demo',
        KeyType='ed25519',
        TagSpecifications=[{'ResourceType': 'key-pair','Tags': [{'Key': 'Name','Value': 'ec2-demo'},]},] )
        # print({key_pair.key_material})
    outfile.write(f"{key_pair.key_material}")
    # Consider adding a print KeyName statement and return it as variable that can be used in the launch_ec2_instance()

create_key_pair()

#Reference: https://www.edureka.co/community/87793/create-a-security-group-and-rules-using-boto3-module

def ec2_security_group(): #creates a default security group for ssh access
    ec2_client = boto3.client("ec2", region_name="us-east-1")
    response = ec2_client.describe_vpcs()
    vpc_id = response.get('Vpcs', [{}])[1].get('VpcId', '') #queries second vpc created for your acct in the us-east-1 region
    try:
        response = ec2_client.create_security_group( #creates the security group
            GroupName='EC2_DEMO',
            Description='SSH Access',
            VpcId=vpc_id)
        security_group_id = response['GroupId']
        print('Security Group Created %s in vpc %s.' % (security_group_id, vpc_id)) 

        response = ec2_client.authorize_security_group_ingress( #creates ssh rule
            GroupId=security_group_id,
            IpPermissions=[
                {'IpProtocol': 'tcp',
                'FromPort': 22,
                'ToPort': 22,
                'IpRanges': [{'CidrIp': '0.0.0.0/0'}]}
            ])
        print('Ingress Successfully Set %s')  
    except ClientError as e:
        print(e)
    return security_group_id

def create_ec2_resource(): #Connects to the ec2 boto3 client with Demo IAM User. 
                           #Change EC2-Admin to your AWS profile name
 
    print("Attempting to create ec2 resource on region: %s" % REGION)
 
    session = boto3.Session(region_name = REGION, profile_name='EC2-Admin')
    # session = boto3.Session(region_name=REGION)
 
    ec2 = session.resource('ec2')
 
    if ec2 is None:
        raise ConnectionError("Could not create ec2 resource!")
 
    return ec2
 
 
def assign_tags_to_instance(ec2, instance_id):
    print("Waiting for instance to be ready ...")
    sleep(7)
    print("Assigning tags to instance " + instance_id)
 
    ec2.create_tags(Resources=[instance_id], Tags=[{'Key': 'Name', 'Value': NAME},
                                                   {'Key': 'Owner', 'Value': OWNER},
                                                   {'Key': 'RunId', 'Value': RUNID}])
    print("Tags assigned to instance successfully!")
 
 
def assign_tags_to_volume(instance):
 
    volumes = instance.volumes.all()
 
    print("Waiting for volume to be attached ...")
    sleep(7)
    for volume in volumes:
        print("Assigning tags to volume %s" % (volume.id))
        volume.create_tags(Tags=[{'Key': 'Name', 'Value': NAME},
                                 {'Key': 'Owner', 'Value': OWNER},
                                 {'Key': 'RunId', 'Value': RUNID}])
        print("Tags applied to volume successfully!")
 
 
def launch_ec2_instance():
 
    ec2 = create_ec2_resource()
 
    blockDeviceMappings = [
        {
            'DeviceName': DEVICE_NAME,
            'Ebs': {
                'DeleteOnTermination': True,
                'VolumeSize': DISK_SIZE_GB,
                'VolumeType': 'gp2'
            }
        },
    ]

    # Create Elastic/Public IP for instance
    if PUBLIC_IP:
        networkInterfaces = [
            {
                'DeviceIndex': 0,
                'Groups': [ec2_security_group()],
                'AssociatePublicIpAddress': True,
                'DeleteOnTermination': True
            }, ]
        instance = ec2.create_instances(ImageId=AMI_IMAGE_ID,
                                        InstanceType=INSTANCE_TYPE,
                                        NetworkInterfaces=networkInterfaces,
                                        UserData=USERDATA_SCRIPT,
                                        MinCount=min_count, MaxCount=max_count,
                                        KeyName=KEY_PAIR_NAME,
                                        BlockDeviceMappings=blockDeviceMappings)
    else:
        instance = ec2.create_instances(ImageId=AMI_IMAGE_ID,
                                        InstanceType=INSTANCE_TYPE,
                                        SecurityGroupIds=[ec2_security_group()],
                                        UserData=USERDATA_SCRIPT,
                                        MinCount=min_count, MaxCount=max_count,
                                        KeyName=KEY_PAIR_NAME,
                                        BlockDeviceMappings=blockDeviceMappings)
    if instance is None:
        raise Exception("Failed to create instance! Check the AWS console to verify creation or try again")
 
    print(f'''
    |-----------------------------------------------------------|
    |                                                           |
    |Instance created and launched successfully!                |
    |Instance id: {instance[0].id}                            |
    |Run the following command: export EC2_ID={instance[0].id}|
    |-----------------------------------------------------------|
    ''')
    assign_tags_to_instance(ec2, instance[0].id)
    assign_tags_to_volume(instance[0])
    return instance[0]

if __name__ == "__main__":
    launch_ec2_instance()

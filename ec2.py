#!/usr/bin/env python3

import boto3
from time import sleep
 
REGION = 'us-east-1'
AMI_IMAGE_ID = 'ami-07d02ee1eeb0c996c'
INSTANCE_TYPE = 't3a.medium'
DISK_SIZE_GB = 20
DEVICE_NAME = '/dev/xvda'
NAME = 'ec2demo002'
OWNER = 'ec2demouser'
RUNID = 'ec2-1'
SUBNET_ID = 'subnet-0883483eb9a1bacfb'
SECURITY_GROUPS_IDS = ['sg-08bb84d24f9e3cd03']
PUBLIC_IP = None
KEY_PAIR_NAME= 'ec2-demo002'
USERDATA_SCRIPT = '''
sudo apt-get update && sudo apt-get install wget git python3 nginx certbot
 
# Install Docker on ec2 instance:
curl -fsSL https://get.docker.com -o get-docker.sh

sh get-docker.sh

sudo usermod -aG docker $USER
'''
 
 
def create_ec2_resource():
 
    print("Attempting to create ec2 ressource on region: %s" % REGION)
 
    session = boto3.Session(region_name = REGION, profile_name='EC2-Admin')
    # session = boto3.Session(region_name=REGION)
 
    ec2 = session.resource('ec2')
 
    if ec2 is None:
        raise ConnectionError("Could not create ec2 resource! Check your connection or aws config!")
 
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
                'SubnetId': SUBNET_ID,
                'Groups': [SECURITY_GROUPS_IDS],
                'AssociatePublicIpAddress': True,
                'DeleteOnTermination': True
            }, ]
        instance = ec2.create_instances(ImageId=AMI_IMAGE_ID,
                                        InstanceType=INSTANCE_TYPE,
                                        NetworkInterfaces=networkInterfaces,
                                        UserData=USERDATA_SCRIPT,
                                        MinCount=1, MaxCount=1,
                                        KeyName=KEY_PAIR_NAME,
                                        BlockDeviceMappings=blockDeviceMappings)
    else:
        instance = ec2.create_instances(ImageId=AMI_IMAGE_ID,
                                        InstanceType=INSTANCE_TYPE,
                                        SubnetId=SUBNET_ID,
                                        SecurityGroupIds=SECURITY_GROUPS_IDS,
                                        UserData=USERDATA_SCRIPT,
                                        MinCount=1, MaxCount=1,
                                        KeyName=KEY_PAIR_NAME,
                                        BlockDeviceMappings=blockDeviceMappings)
    if instance is None:
        raise Exception("Failed to create instance! Check the AWS console to verify creation or try again")
 
    print("Instance created and launched successfully!")
    print("#### Instance id: " + instance[0].id)
 
    assign_tags_to_instance(ec2, instance[0].id)
    assign_tags_to_volume(instance[0])
 
    return instance[0]
 
 
if __name__ == "__main__":
    launch_ec2_instance()

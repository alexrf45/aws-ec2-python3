"""
A simple script for creating an ec2 instance with a security group and key pair
"""

#!/usr/bin/env python3
import logging
from time import sleep # allows script execution to pause as AWS CLI execution
                       # on AWS servers are not always instant.
import boto3
import boto3auth
from botocore.exceptions import ClientError

logger = logging.getLogger()
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s: %(levelname)s: %(message)s')

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
USERDATA_SCRIPT = '''#!/bin/bash
apt-get update && apt-get install -y wget git python3 nginx certbot
# Install Docker on ec2 instance:
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
sudo usermod -aG docker $USER
. ~/.bashrc
'''
MIN_COUNT = 1 #Minimum number of ec2 instances created
MAX_COUNT = 1 #Maximum number of ec2 instances created


## This function creates a keypair and saves it in the current directory as a .pem file
def create_key_pair():
    """
    This function creates a keypair and associates it with the AWS account.
    """
    ec2_client = boto3.resource("ec2", region_name="us-east-1")
    outfile = open('ec2demo.pem', 'w',encoding='UTF-8')
    key_pair = ec2_client.create_key_pair(
        KeyName='ec2-demo',
        KeyType='ed25519',
        TagSpecifications=[
            {'ResourceType': 'key-pair',
            'Tags': [
                {'Key': 'Name','Value': 'ec2-demo'},
                ]
            },
        ]
    )
    outfile.write(f"{key_pair.key_material}")
    # Consider adding a print KeyName statement and return
    # it as variable that can be used in the launch_ec2_instance()

#Reference:
# https://www.edureka.co/community/87793/create-a-security-group-and-rules-using-boto3-module

def ec2_security_group():
    """
    This function creates a default security group for ssh access
    """
    ec2_client = boto3.client("ec2", region_name="us-east-1")
    response = ec2_client.describe_vpcs()
    vpc_id = response.get('Vpcs', [{}])[1].get('VpcId', '')
    #queries second vpc created for your acct in the us-east-1 region
    try:
        response = ec2_client.create_security_group( #creates the security group
            GroupName='EC2_DEMO',
            Description='SSH Access',
            VpcId=vpc_id)
        security_group_id = response['GroupId']
        print(f'Security Group Created {security_group_id} in vpc {vpc_id}.' )

        response = ec2_client.authorize_security_group_ingress( #creates ssh rule
            GroupId=security_group_id,
            IpPermissions=[
                {'IpProtocol': 'tcp',
                'FromPort': 22,
                'ToPort': 22,
                'IpRanges': [{'CidrIp': '0.0.0.0/0'}]}
            ])
        print('Ingress Successfully Set')
    except ClientError as client_error:
        print(client_error)
    return security_group_id

def create_ec2_resource():
    """
    Connects to the ec2 boto3 client with Demo IAM User.
    Change EC2-Admin to your AWS profile name
    """
    logger.info('Attempting to create ec2 resource on region: %s', REGION)

    session = boto3auth.Boto3Auth()
    ec2 = session.auth('ec2')

    if ec2 is None:
        raise ConnectionError("Could not create ec2 resource!")

    return ec2


def assign_tags_to_instance(ec2, instance_id):
    """
    Assigns tags to the ec2 instance.
    """
    print("Waiting for instance to be ready ...")
    sleep(7)
    print("Assigning tags to instance " + instance_id)

    ec2.create_tags(Resources=[instance_id], Tags=[{'Key': 'Name', 'Value': NAME},
                                                   {'Key': 'Owner', 'Value': OWNER},
                                                   {'Key': 'RunId', 'Value': RUNID}])
    print("Tags assigned to instance successfully!")


def assign_tags_to_volume(instance):
    """
    Assigns tags to the volumes created for the ec2 instance.
    """

    volumes = instance.volumes.all()

    print("Waiting for volume to be attached ...")
    sleep(7)
    for volume in volumes:
        print(f'Assigning tags to volume {volume.id}')
        volume.create_tags(Tags=[{'Key': 'Name', 'Value': NAME},
                                 {'Key': 'Owner', 'Value': OWNER},
                                 {'Key': 'RunId', 'Value': RUNID}])
        print("Tags applied to volume successfully!")

def launch_ec2_instance():
    """
    Creates the EC2 instance using all the info generated by the previous functions
    """

    ec2 = create_ec2_resource()

    BlockDeviceMappings = [
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
        NetworkInterfaces = [
            {
                'DeviceIndex': 0,
                'Groups': [ec2_security_group()],
                'AssociatePublicIpAddress': True,
                'DeleteOnTermination': True
            }, ]
        instance = ec2.create_instances(ImageId=AMI_IMAGE_ID,
                                        InstanceType=INSTANCE_TYPE,
                                        NetworkInterfaces=NetworkInterfaces,
                                        UserData=USERDATA_SCRIPT,
                                        MinCount=MIN_COUNT, MaxCount=MAX_COUNT,
                                        KeyName=KEY_PAIR_NAME,
                                        BlockDeviceMappings=BlockDeviceMappings)
    else:
        instance = ec2.create_instances(ImageId=AMI_IMAGE_ID,
                                        InstanceType=INSTANCE_TYPE,
                                        SecurityGroupIds=[ec2_security_group()],
                                        UserData=USERDATA_SCRIPT,
                                        MinCount=MIN_COUNT, MaxCount=MAX_COUNT,
                                        KeyName=KEY_PAIR_NAME,
                                        BlockDeviceMappings=BlockDeviceMappings)
    if instance is None:
        raise Exception("""
        Failed to create instance! Check the AWS console to verify creation or try again
        """)

    # print(f'''
    # |-----------------------------------------------------------|
    # |                                                           |
    # |Instance created and launched successfully!                |
    # |Instance id: {instance[0].id}                            |
    # |Run the following command: export EC2_ID={instance[0].id}|
    # |-----------------------------------------------------------|
    # ''')
    logger.info('Instance created and launched successfully!')
    logger.info('Instance id: %s', instance[0].id)
    logger.info('Run the following command: export EC2_ID=%s', instance[0].id)
    assign_tags_to_instance(ec2, instance[0].id)
    assign_tags_to_volume(instance[0])
    return instance[0]

if __name__ == "__main__":
    create_key_pair()
    launch_ec2_instance()

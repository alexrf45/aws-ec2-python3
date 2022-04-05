import logging
import boto3
from botocore.exceptions import ClientError
import json

AWS_REGION = 'us-east-1'

# logger config
logger = logging.getLogger()
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s: %(levelname)s: %(message)s')

vpc_client = boto3.client("ec2", region_name=AWS_REGION)


def describe_vpc_attribute(vpc_id, attribute):
    """
    Describes the specified attribute of the specified VPC.
    """
    try:
        response = vpc_client.describe_vpc_attribute(Attribute=attribute,
                                                     VpcId=vpc_id)

    except ClientError:
        logger.exception('Could not describe a vpc attribute.')
        raise
    else:
        return response

describe_vpc_attribute(vpc_id, attribute)
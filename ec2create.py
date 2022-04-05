import boto3

def create_instance():
    ec2_client = boto3.client("ec2", region_name="us-east-1")
    instances = ec2_client.run_instances(
        ImageId="ami-03190fe20ef6b1419",
        MinCount=1,
        MaxCount=1,
        InstanceType="t4g.nano",
        KeyName = input("enter key pair name:")
    )

    print(instances["Instances"][0]["InstanceId"])
    

create_instance()



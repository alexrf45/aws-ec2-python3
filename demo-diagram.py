from diagrams import Cluster, Diagram
from diagrams.aws.compute import EC2Instance
from diagrams.aws.network import InternetGateway
from diagrams.aws.network import VPCElasticNetworkInterface


with Diagram("EC2-Demo", direction="LR", outformat="pdf", show=False):
   

    with Cluster("AWS"): #AWS environment
        ig = InternetGateway('default ig')
        with Cluster("Default VPC 172.31.0.0/16"): #default VPC AWS creates for you
            eis_int = VPCElasticNetworkInterface("Elastic IP")
            with Cluster("default subnet 1: 172.31.16.0/20 "):
                ec2_demo = EC2Instance("ec2-demo")
    ig >> eis_int >> ec2_demo #network flow from internet gateway
                              # to ec2 instance
from aws_cdk import core as cdk
# For consistency with other languages, 
# `cdk` is the preferred import name for the CDK's core module.
from aws_cdk import (
    aws_ec2,
)

VPC_CIDR="10.100.0.0/16"

class DemoVpcStack(cdk.Stack):

    def __init__(self, scope: cdk.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.vpc = aws_ec2.Vpc(self, "bi-demo-vpc", 
            cidr=VPC_CIDR,
            max_azs=2,
            subnet_configuration=[
                aws_ec2.SubnetConfiguration(
                    name= 'subnet-public',
                    subnet_type=aws_ec2.SubnetType.PUBLIC,
                    cidr_mask=20
                ),
                aws_ec2.SubnetConfiguration(
                    name= 'subnet-private',
                    subnet_type=aws_ec2.SubnetType.PRIVATE,
                    cidr_mask=20
                ),
                aws_ec2.SubnetConfiguration(
                    name= 'subnet-isolated',
                    subnet_type=aws_ec2.SubnetType.ISOLATED,
                    cidr_mask=20
                )
            ]
        )

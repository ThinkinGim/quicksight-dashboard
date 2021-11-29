from aws_cdk import core as cdk
# For consistency with other languages, 
# `cdk` is the preferred import name for the CDK's core module.
from aws_cdk import (
    aws_rds,
    aws_ec2,
)

class ServiceDBStack(cdk.Stack):

    def __init__(self, scope: cdk.Construct, construct_id: str, vpc:aws_ec2.Vpc, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        db_subnet_group = aws_rds.SubnetGroup(self, 'bi-demo-db-subnets',
            description='bi-demo-db-subnets',
            vpc=vpc,
            removal_policy=cdk.RemovalPolicy.DESTROY,
            vpc_subnets=aws_ec2.SubnetSelection(subnets=vpc.isolated_subnets)
        )

        db_security_group = aws_ec2.SecurityGroup(self, 'bi-demo-db-sg',
            vpc=vpc
        )

        db_security_group.add_ingress_rule(
            peer=aws_ec2.Peer.ipv4(vpc.vpc_cidr_block),
            connection=aws_ec2.Port(
                protocol=aws_ec2.Protocol.TCP,
                string_representation="to allow from the vpc internal",
                from_port=3306,
                to_port=3306
            )
        )

        db_param_group = aws_rds.ParameterGroup(self, 'bi-demo-db-param',
            engine=aws_rds.DatabaseClusterEngine.AURORA_MYSQL
        )
        db_param_group.add_parameter("performance_schema", "1")

        aws_rds.DatabaseCluster(self, 'bi-demo-db',
            engine=aws_rds.DatabaseClusterEngine.aurora_mysql(version=aws_rds.AuroraMysqlEngineVersion.VER_2_07_1),
            instance_props=aws_rds.InstanceProps(
                vpc=vpc,
                instance_type=aws_ec2.InstanceType.of(instance_class=aws_ec2.InstanceClass.BURSTABLE3, instance_size=aws_ec2.InstanceSize.MEDIUM),
                security_groups=[db_security_group]
            ),
            instances=1,
            subnet_group=db_subnet_group,
            parameter_group=db_param_group,
            removal_policy=cdk.RemovalPolicy.DESTROY
        )

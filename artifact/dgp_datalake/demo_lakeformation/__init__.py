from aws_cdk import core as cdk
from aws_cdk import (
    aws_s3,
    aws_s3_deployment,
    aws_iam,
    aws_ec2,
    aws_glue,
    aws_lakeformation,
)

import boto3

def setDefaultPermissions():
    boto3_client = boto3.client('lakeformation')
    boto3_response = boto3_client.get_data_lake_settings()

    db_default_permissions = boto3_response['DataLakeSettings']['CreateDatabaseDefaultPermissions']
    table_default_permissions = boto3_response['DataLakeSettings']['CreateTableDefaultPermissions']

    if db_default_permissions or table_default_permissions:
        print(f"default_permissions is not empty. {db_default_permissions}, {table_default_permissions}")
        boto3_client.put_data_lake_settings(
            DataLakeSettings={
                "CreateDatabaseDefaultPermissions": [],
                "CreateTableDefaultPermissions": [],
                'DataLakeAdmins': boto3_response['DataLakeSettings']['DataLakeAdmins']
            }
        )


class DemoLakeformationStack(cdk.Stack):

    def __init__(self, scope: cdk.Construct, construct_id: str, datalakes_storage:aws_s3.Bucket, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        app_id = self.node.try_get_context("app_id")
        setDefaultPermissions()
        
        # https://docs.aws.amazon.com/athena/latest/ug/tables-databases-columns-names.html
        # Special characters other than underscore (_) are not supported in Athena query.
        
        glue_db = aws_glue.Database(self, f'{app_id}-lf-database',
            database_name="demogopdb",
            location_uri=f"s3://{datalakes_storage.bucket_name}"
        )
        
        aws_lakeformation.CfnResource(self, f'{app_id}-lf-location',
            resource_arn=datalakes_storage.bucket_arn,
            use_service_linked_role=True,
        )

        glue_role = aws_iam.Role(self, f'{app_id}-lf-gluerole',
            assumed_by=aws_iam.CompositePrincipal(
                aws_iam.ServicePrincipal("glue.amazonaws.com"),
                aws_iam.ServicePrincipal("lakeformation.amazonaws.com"),
            )
        )

        glue_role.add_managed_policy(
            aws_iam.ManagedPolicy.from_managed_policy_arn(self, 'bi-demo-glue-servicepolicy', 
                managed_policy_arn='arn:aws:iam::aws:policy/service-role/AWSGlueServiceRole'
            )
        )

        glue_role.add_to_policy(aws_iam.PolicyStatement(
            effect=aws_iam.Effect.ALLOW,
            actions=["s3:*"],
            resources=[datalakes_storage.bucket_arn, f"{datalakes_storage.bucket_arn}/*"]
        ))

        glue_role.add_to_policy(aws_iam.PolicyStatement(
            effect=aws_iam.Effect.ALLOW,
            actions=[
                "lakeformation:*",
                "cloudtrail:DescribeTrails",
                "cloudtrail:LookupEvents",
                "glue:GetDatabase",
                "glue:GetDatabases",
                "glue:CreateDatabase",
                "glue:UpdateDatabase",
                "glue:DeleteDatabase",
                "glue:GetConnections",
                "glue:SearchTables",
                "glue:GetTable",
                "glue:CreateTable",
                "glue:UpdateTable",
                "glue:DeleteTable",
                "glue:GetTableVersions",
                "glue:GetPartitions",
                "glue:GetTables",
                "glue:GetWorkflow",
                "glue:ListWorkflows",
                "glue:BatchGetWorkflows",
                "glue:DeleteWorkflow",
                "glue:GetWorkflowRuns",
                "glue:StartWorkflowRun",
                "glue:GetWorkflow",
                "s3:ListBucket",
                "s3:GetBucketLocation",
                "s3:ListAllMyBuckets",
                "s3:GetBucketAcl",
                "iam:ListUsers",
                "iam:ListRoles",
                "iam:GetRole",
                "iam:GetRolePolicy"
            ],
            resources=["*"]
        ))

        glue_role.add_to_policy(aws_iam.PolicyStatement(
            effect=aws_iam.Effect.DENY,
            actions=[
                "lakeformation:PutDataLakeSettings"
            ],
            resources=["*"]
        ))

        glue_role.add_to_policy(aws_iam.PolicyStatement(
            actions=["iam:PassRole"],
            resources=[glue_role.role_arn]
        ))

        DemoLakeformationPermissionStack(self, f'{app_id}-lf-permissions-stack',
            glue_role_arn=glue_role.role_arn,
            glue_db_name=glue_db.database_name
        )

        # aws_glue.Connection(self, "bi-demo-glue-conn",
        #     type=aws_glue.ConnectionType.JDBC,
        #     connection_name="bi-demo-glue-conn",
        #     security_groups=[aws_ec2.SecurityGroup.from_security_group_id(self, 'default-sg', security_group_id=vpc.vpc_default_security_group)],
        #     # subnet=aws_ec2.SubnetSelection(subnet_type=aws_ec2.SubnetType.PUBLIC),
        #     properties={
        #         'JDBC_CONNECTION_URL': 'jdbc:mysql://host:3306/dbname',
        #         'USERNAME': 'user',
        #         'PASSWORD': 'password',
        #     }
        # )
        # scheme of connection properties can refer to Output statement of CLI to get metadata
        # https://docs.aws.amazon.com/cli/latest/reference/glue/get-connection.html

class DemoLakeformationPermissionStack(cdk.NestedStack):

    def __init__(
        self,
        scope: cdk.Construct,
        construct_id: str,
        glue_role_arn: str,
        glue_db_name: str,
        **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        app_id = self.node.try_get_context("app_id")

        aws_lakeformation.CfnPermissions(self, f'{app_id}-lf-permissions',
            data_lake_principal=aws_lakeformation.CfnPermissions.DataLakePrincipalProperty(
                data_lake_principal_identifier=glue_role_arn
            ),
            resource=aws_lakeformation.CfnPermissions.ResourceProperty(
                database_resource=aws_lakeformation.CfnPermissions.DatabaseResourceProperty(
                catalog_id=cdk.Stack.of(self).account,
                name=glue_db_name),
            ),
            permissions=["ALL", "CREATE_TABLE"]
        )




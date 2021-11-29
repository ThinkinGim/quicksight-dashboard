from aws_cdk import core as cdk
from aws_cdk import (
    aws_s3,
    aws_s3_deployment,
    aws_iam,
    aws_lakeformation,
)

class DatalakePermissionsStack(cdk.Stack):

    def __init__(self, scope: cdk.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        demogo_marketing_user = aws_iam.User(self, 'demo-user-marketer',
            user_name="demogo-marketing"
        )

        demogo_marketing_user.add_managed_policy(
            aws_iam.ManagedPolicy.from_managed_policy_arn(self, 'demogo-databrew', 
                managed_policy_arn='arn:aws:iam::aws:policy/AwsGlueDataBrewFullAccessPolicy'
            )
        )

        # aws_lakeformation.CfnPermissions(self, 'bi-demo-lf-permission',
        #     data_lake_principal=aws_lakeformation.CfnPermissions.DataLakePrincipalProperty(
        #         data_lake_principal_identifier=glue_role.role_arn
        #     ),
        #     resource=aws_lakeformation.CfnPermissions.ResourceProperty(
        #         database_resource=aws_lakeformation.CfnPermissions.DatabaseResourceProperty(
        #         catalog_id=ACCOUNT_ID,
        #         name=GLUE_DB_NAME),
        #     ),
        #     permissions=["ALL", "CREATE_TABLE"]
        # )
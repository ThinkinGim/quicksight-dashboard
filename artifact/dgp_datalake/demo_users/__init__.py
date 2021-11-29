from aws_cdk import core as cdk
from aws_cdk import (
    aws_iam,
)

class DemoUsersStack(cdk.Stack):

    def __init__(self, scope: cdk.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        app_id = self.node.try_get_context('app_id')

        demo_marketer = aws_iam.User(self, f'{app_id}-demouser-marketer',
            user_name="demo-marketer"
        )

        demo_marketer.add_managed_policy(
            aws_iam.ManagedPolicy.from_managed_policy_arn(self, f'{app_id}-demouser-marketer-policy', 
                managed_policy_arn='arn:aws:iam::aws:policy/AwsGlueDataBrewFullAccessPolicy'
            )
        )

        demo_admin = aws_iam.User(self, f'{app_id}-demouser-admin',
            user_name="demo-adminuser"
        )

        cdk.CfnOutput(self, 'Demo-user-marketer', value=demo_marketer.user_name)
        cdk.CfnOutput(self, 'Demo-user-admin', value=demo_admin.user_name)
        
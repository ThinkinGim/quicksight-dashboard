from aws_cdk import core as cdk
from aws_cdk import (
    aws_s3,
    aws_s3_deployment,
)

class DatalakeStorageStack(cdk.Stack):

    def __init__(
        self,
        scope: cdk.Construct,
        construct_id: str,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        app_id = self.node.try_get_context("app_id")

        self.datalake_bucket = aws_s3.Bucket(self, f'{app_id}-lf-bucket',
            auto_delete_objects=True,
            removal_policy=cdk.RemovalPolicy.DESTROY)

        aws_s3_deployment.BucketDeployment(self, f'{app_id}-lf-bucket-srcdata',
            sources=[aws_s3_deployment.Source.asset("./assets/sample_data")],
            destination_bucket=self.datalake_bucket,
            destination_key_prefix="source_data"
        )

        cdk.CfnOutput(self, "BucketName", value=self.datalake_bucket.bucket_name)

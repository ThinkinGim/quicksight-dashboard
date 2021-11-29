#!/usr/bin/env python3

from aws_cdk import core as cdk
from artifact.dgp_datalake.datalakes_storage import DatalakeStorageStack
from artifact.dgp_datalake.demo_users import DemoUsersStack
from artifact.dgp_datalake.demo_lakeformation import DemoLakeformationStack

app = cdk.App()
app_id = app.node.try_get_context('app_id')

# vpc_stack = VpcStack(app, "demo-vpc")
# ServiceDBStack(app, "demo-servicedb", vpc=vpc_stack.vpc)
# datalake = DatalakeStack(app, "demo-lakeformation",vpc=vpc_stack.vpc)
# DatalakePermissionsStack(app, "demo-users")

lakes_storage = DatalakeStorageStack(app, f'{app_id}-1-lakestorage')
DemoUsersStack(app, f'{app_id}-2-demousers')
DemoLakeformationStack(app, f'{app_id}-3-lakeformation', datalakes_storage=lakes_storage.datalake_bucket)

app.synth()

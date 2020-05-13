from aws_cdk import (
    aws_iam as iam,
    aws_sqs as sqs,
    aws_sns as sns,
    aws_sns_subscriptions as subs,
    aws_codecommit as code_co,
    aws_codepipeline as codepipeline,
    aws_codepipeline_actions as codepipeline_actions,
    aws_codebuild as codebuild,
    aws_sam as sam,
    aws_dynamodb as ddb,
    aws_lambda as _lambda,
    aws_kms as kms,
    aws_secretsmanager as sm,
    aws_amplify as amplify,
    aws_s3 as s3,
    core,
)

class SumerianStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        bcuket_name='eventhelper-vtc-bucket'
        my_bucke=s3.Bucket(self,bcuket_name)

        eventhelper_comprehend_table= ddb.Table(self,"eventhelper_comprehend",partition_key={   #create a user table
            'name':'Boothname', 'type': ddb.AttributeType.STRING},
            sort_key={'name':'Time','type':ddb.AttributeType.NUMBER}
        
        )
        
        eventhelper_rekognition_table= ddb.Table(self,"eventhelper_rekognition",partition_key={   #create a user table
            'name':'Boothname', 'type': ddb.AttributeType.STRING},
            sort_key={'name':'Time','type':ddb.AttributeType.NUMBER}
        
        )
        eventhelper_workshop_participant_table= ddb.Table(self,"eventhelper_workshop_participant",partition_key={   #create a user table
            'name':'Workshop', 'type': ddb.AttributeType.STRING},
            sort_key={'name':'Username','type':ddb.AttributeType.STRING}

        )
        workshopList_table= ddb.Table(self,"workshopList",partition_key={
            'name':'Workshop', 'type': ddb.AttributeType.STRING})
        

        eventhelper_lambda_role=iam.Role(self,'eventhelper_connect_role',assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"))
        eventhelper_lambda_role.add_to_policy(iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            resources=["*"],actions=['*']))
        
        eventhelper_connect_lambda=_lambda.Function(self,'eventhelper-connect',
            runtime=_lambda.Runtime.PYTHON_3_7,code=_lambda.Code.asset("./cdkdeploy/eventhelper_connect_lambda/lambda/"),
            handler="lambda.lambda_handler",
            timeout=core.Duration.seconds(300),
            environment=dict(
                    ContactFlowId= 'None',
                    InstanceId='None',
                    SourcePhoneNumber='None'
            ),role=eventhelper_lambda_role)
        
        eventhelper_rekognition_table.grant_read_write_data(eventhelper_connect_lambda)
            
            
        eventhelper_table_comprehend_rekognition_lambda=_lambda.Function(self,'eventhelper-table-comprehend-rekognition',
            runtime=_lambda.Runtime.PYTHON_3_7,code=_lambda.Code.asset("./cdkdeploy/eventhelper_table_comprehend_rekognition_lambda/lambda/"),
            handler="lambda.lambda_handler",
            timeout=core.Duration.seconds(300),
            environment=dict(
                    Bucket= my_bucke.bucket_name)
            ,role=eventhelper_lambda_role)
        
        eventhelper_comprehend_table.grant_read_write_data(eventhelper_table_comprehend_rekognition_lambda)
    
            
        eventhelper_dynamodb_update_lambda=_lambda.Function(self,'eventhelper_dynamodb_update_lambda',
            runtime=_lambda.Runtime.PYTHON_3_7,code=_lambda.Code.asset("./cdkdeploy/eventhelper_dynamodb_update/lambda"),
            handler="lambda.lambda_handler",
            timeout=core.Duration.seconds(300),
            role=eventhelper_lambda_role)
    
        eventhelper_workshop_participant_table.grant_read_write_data(eventhelper_dynamodb_update_lambda)
        workshopList_table.grant_read_write_data(eventhelper_dynamodb_update_lambda)
        
        eventhelper_callout_lambda=_lambda.Function(self,'eventhelper_callout_lambda',
            runtime=_lambda.Runtime.PYTHON_3_7,code=_lambda.Code.asset("./cdkdeploy/eventhelper_callout_lambda/lambda"),
            handler="lambda.lambda_handler",
            timeout=core.Duration.seconds(300),
            role=eventhelper_lambda_role)
            
        eventhelper_workshop_participant_table.grant_read_write_data(eventhelper_dynamodb_update_lambda)
        workshopList_table.grant_read_write_data(eventhelper_dynamodb_update_lambda)
    
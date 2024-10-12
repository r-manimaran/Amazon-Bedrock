#Lambda handler function to Auto Sync Bedrock Knowledge Base
import json
import boto3
import os
import logging

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger.info('Loading function')

bedrockClient = boto3.client('bedrock-agent')

def lambda_handler(event, context):
    DATA_SOURCE_ID = os.environ['DATA_SOURCE_ID']
    KNOWLEDGE_BASE_ID = os.environ['KNOWLEDGE_BASE_ID']
     
    # Call Bedrock Agent to sync the Knowledge Base
    response = bedrockClient.start_ingestion_job(
        knowledgeBaseId=KNOWLEDGE_BASE_ID,
        dataSourceId=DATA_SOURCE_ID
    )
    
    logger.info(response)
    logger.info('Document synced successfully')
    return {
        'statusCode': 200,
        'body': json.dumps('response')
    }
import os
import boto3


boto3_session = boto3.session.Session()
bedrock_agent_runtime_client = boto3.client('bedrock-agent-runtime')

# Retreive the Knowledge base ID from evironment Variables
def get_kb_id_from_env():
    kb_id = os.environ.get('KNOWLEDGE_BASE_ID')
    if not kb_id:
        raise ValueError("KNOWLEDGE_BASE_ID environment variable is not set.")
    return kb_id

kb_id = get_kb_id_from_env()

def retrieve(input_text, kbId):
    print("Retrieving knowledge base information for text:", input_text, "from knowledge base:", kbId )
    response = bedrock_agent_runtime_client.retrieve(
        retrievalQuery={
            'text': input_text
        },
        knowledgeBaseId=kbId,             
        retrievalConfiguration={
            'vectorSearchConfiguration': {
                'numberOfResults': 5  # Adjust the number of results as needed
                #'filter':{}, # uncomment and specify filters if needed
                #'overrideSearchType': 'HYBRID' # uncomment and specify the search type if needed
            }
        }
    )
    print("Retrieved response:", response)
    return response
   

def lambda_handler(event, context):
    if 'question' not in event:
        return {
            'statusCode': 400,
            'body': 'Missing required parameter: question'
        }
    query = event['question']   
    response = retrieve(query, kb_id)
    print("Final response:", response)
    return {
        'statusCode': 200,
        'body': {
            "answer": response,
            "question": query.strip()
        }
    }
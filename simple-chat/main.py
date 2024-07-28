import boto3
import json

bedrock_runtime = boto3.client('bedrock-runtime', region_name='us-east-1')
prompt = "Write a one sentence summary of North Carolina"

kwargs = {
    "modelId":"amazon.titan-text-lite-v1",
    "contentType": "application/json",
    "accept": "*/*",
    "body": json.dumps({"inputText": prompt})
}
response = bedrock_runtime.invoke_model(**kwargs)
print(response)
response_body = json.loads(response.get("body").read())
print(json.dumps(response_body,indent=4))
print(response_body["results"][0]["outputText"])
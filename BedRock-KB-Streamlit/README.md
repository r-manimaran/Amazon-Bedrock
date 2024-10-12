# RAG App using Amazon BedRock KnowledgeBase and Streamlit
Key tasks here are 
1. Upload the pdf file to S3 bucket
2. Enable/Get access to the AI models in Amazon Bedrock
3. Create a knowledge base(KB) and use Titan Embedding to embed the pdf file from S3 Datasource
4. Test the Knowledge base
5. Note down the KB Id, which we need to use it in Streamlit app.
6. In the Amazon Bedrock note down the Model ARN which needs to be used in Streamlit app.

### Model Id and ARN
![alt text](images\image.png)

### Streamlit app
- pip install the required packages (refer requirements.txt)
- using boto3 get the client bedrock-agent-runtime
- Used retrieve_and_generate API
- This API retrieves most relevant information based on user's question from the Knowledge base and provide a response.
- The response is pass to LLM along with query to generate the required response

### Streamlit chat
![alt text](images\image3.png)
![alt text](images\image2.png)

![alt text](images\image-1.png)

## Upload File to S3 using Streamlit

![alt text](images\image4.png)

![alt text](images\image5.png)
upload to S3 folder (prefix)

![alt text](images\image6.png)

## Sync KB when Fileupload in S3

![alt text](images\image7.png)

![alt text](images\image8.png)

## Configure Trigger in Lambda to auto-sync Datasource in KB
- When new files are uploaded to S3, this will trigger the lambda function to automatically sync the embeddings to KB.
  
![alt text](images\image-2.png)

![alt text](images\image9.png)
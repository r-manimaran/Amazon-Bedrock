# Amazon BedRock RAG with Lambda and FastAPI

## Architecture



### Knowledge Base
1. The Pdf document(Git-Guide.pdf) is uploaded to S3
2. In the Amazon BedRock get access to Models using the Model access option.
3. On the Knowledge Base, create a new knowlege base
   1. Select the DataSource as S3 and point to the S3 folder where the pdf file exists.
   2. Select the Titan embeddings
   3. Select default Vector DB
   4. Select default chunking option
4. Click Sync to create embeddings and Vector store for the document gets chucked and create embeddings
5. Test the Response in the Knowledge Base itself.
6. Note the Knowledge_Base Id, which will be used in the Lambda function

![alt text](images\image-5.png)

![alt text](images\image-6.png)

![alt text](images\image-7.png)

![alt text](images\image-8.png)

![alt text](images\image-9.png)
### Create a Lambda function.
1. Use Boto3 to create client and connect to Knowledge Base
2. Define the Environment variable KNOWLEDGE_BASE_ID
3. Assign a Lambda execution role
4. Edit the Role and add Access to Amazon BedRock
5. Deploy the Lambda fuction and perform a Test
6. This will return the relevant records from Knowledge Base
7. Change the Timeout to 1:15 sec, just to avoid timeout incase.
   
![alt text](images\image-3.png)

![alt text](images\image-4.png)

### Create Python FAST API
1. This Fast API will access the Lambda function and get the relevant records for the question from the Knowledge Base 
2. Used OpenAI LLM ChatModel with a prompt.
3. The user question along with the relevant records received from Lambda function will be passed to LLM
4. The LLM provides the final answer.


## Fast API Endpoint
- main.py contains the FastAPI code with endpoint
  ```command
  Run the FastAPI app
  > uvicorn main:app -reload
  ```

![alt text](images\image.png)

![alt text](images\image-1.png)

### Response
![alt text](images\image-2.png)

### Deploy in render
- We can deploy the FastAPI in the render. 
- Use the WebServices option and select the github source
  ![alt text](images\image-10.png) 
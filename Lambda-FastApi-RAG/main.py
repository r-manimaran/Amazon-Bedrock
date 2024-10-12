from fastapi import FastAPI,  HTTPException, status, Query
from fastapi.responses import JSONResponse, RedirectResponse

import boto3
import json
import os

from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

from dotenv import load_dotenv
load_dotenv()

app = FastAPI()

lambda_client = boto3.client('lambda')
print(lambda_client)

def get_context(question:str):
    try:
        #invoke the Lamda function
        response = lambda_client.invoke(
            FunctionName=os.environ.get('LAMBDA_FUNCTION_NAME'),
            InvocationType='RequestResponse',
            Payload=json.dumps({'question': question})
        )
        #parse the response
        response_payload = response['Payload'].read()
        response_payload_dict = json.loads(response_payload)
        
        #Navigate to the retrieval Results
        results = response_payload_dict['body']['answer']['retrievalResults']
        print(results)

        #initialize an empty string to store the extracted paragraph
        extracted_paragraph = ""

        #iterate through the results and extract the paragraph
        for result in results:
            text = result['content']['text']
            extracted_paragraph += text+ " "
        # return the concatenated paragraph
        return {"response":extracted_paragraph.strip()}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    

def get_answer_from_kb(query:str):
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

    prompt = PromptTemplate(
        input_variables=["context", "question"],
        template="""
        You are a helpful assistant. Answer the question based on the context below. 
        If you can't find the answer in the context, just say "I don't know".
        Context: {context}
        Question: {question}
        """
    )
    chain = LLMChain(llm=llm, prompt=prompt)
    context = get_context(query)
    print(context)
    result = chain.run({"context":context, "question":query})
    return result

#Fast API endpoint
@app.post("/chat_with_KB")
def chat_with_KB(question: str = Query(..., description="The question to ask")):
    try:
        answer = get_answer_from_kb(question)
        return JSONResponse(content= answer, status_code=status.HTTP_200_OK)
    except HTTPException as e:
        return JSONResponse(status_code=e.status_code, content={"error": e.detail})
    
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

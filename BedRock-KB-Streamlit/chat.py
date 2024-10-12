import boto3
import streamlit as st
import json
import json
import json
import os
from dotenv import load_dotenv

load_dotenv()
#Get the config from env file
KNOWLEDGE_BASE_ID = os.getenv('KNOWLEDGE_BASE_ID')


st.set_page_config(page_title="Amazon Bedrock Demo", layout="wide")
st.title("Amazon Bedrock Demo")
st.subheader("RAG with Amazon BedRock Knowledge Base",divider='rainbow')

#Define the chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

#display the chat history
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["text"])

#initialize the Bedrock client
bedrock = boto3.client('bedrock-agent-runtime', region_name='us-east-1')
model_id = 'anthropic.claude-v2:1'

#define a method to get answers for the question
def get_answer(question):
    #invoke the model
    response = bedrock.retrieve_and_generate(        
        input={
            'text': question
        },
        retrieveAndGenerateConfiguration={
            'knowledgeBaseConfiguration': {
                'knowledgeBaseId': KNOWLEDGE_BASE_ID,                
                'modelArn': 'arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-v2:1'
            },                
            'type':'KNOWLEDGE_BASE',           
            
        }
    )
    return response
    
#Form input
question = st.chat_input("Ask a question")
if question:
    with st.chat_message("user"):
        st.markdown(question)    
    st.session_state.chat_history.append({"role": "user", "text": question})

    #get the answer
    st.chat_message("assistant").write("Thinking...")
    answer = get_answer(question)
    response = answer['output']['text']
    with st.chat_message("assistant"):
        st.markdown(response)   
    st.session_state.chat_history.append({"role": "assistant", "text": response})

    if len(answer['citations'][0]['retrievedReferences'])!=0:
        context = answer['citations'][0]['retrievedReferences'][0]['content']['text']
        doc_url = answer['citations'][0]['retrievedReferences'][0]['location']['s3Location']['uri']

        st.markdown(f"<span style='color:blue'>Context: {context}</span>", unsafe_allow_html=True)
        st.markdown(f"<span style='color:blue'>Source: {doc_url}</span>", unsafe_allow_html=True)
        
    else:
        st.markdown(f"<span style='color:red'>No Context</span>", unsafe_allow_html=True)
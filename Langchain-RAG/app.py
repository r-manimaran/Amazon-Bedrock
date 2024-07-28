import json
import os
import boto3
import logging
# imports for Embeddings and LLM
from langchain_community.embeddings import BedrockEmbeddings


#used for data ingections
import numpy as np

# imports for load documents and text splitting
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFDirectoryLoader

#imports for vector store
from langchain_community.vectorstores import FAISS

# imports for LLM
from langchain_community.llms import Bedrock
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA

#imports for Streamlit
import streamlit as st

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)
logger.info("Loading function")

# use Amazon Titan for embedding
logger.info("Loading bedrock runtime and Amazon Titan Embeddings")
bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')
bedrock_embeddings = BedrockEmbeddings(model_id="amazon.titan-embed-text-v1", 
                                       client=bedrock)

#helper methods
# Load documents from a directory
def load_documents_from_directory(directory):
    logger.info("Loading documents from directory")
    loader = PyPDFDirectoryLoader(directory)
    documents = loader.load()
    return documents

# Split documents into chunks
def split_documents(documents):
    logger.info("Splitting documents into chunks")
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=10000, chunk_overlap=1000)
    texts = text_splitter.split_documents(documents)
    return texts

# Create vector store from documents
def create_vector_store(texts):
    logger.info("Creating vector store from documents")
    vectorstore = FAISS.from_documents(texts, bedrock_embeddings)
    return vectorstore

# create LLM model
def create_llm():
    logger.info("Creating LLM")
    modelId = "amazon.titan-text-lite-v1"
    accept = 'application/json'
    contentType = 'application/json'
    llm = Bedrock(model_id=modelId, client=bedrock, model_kwargs={'maxTokenCount': 512})
    return llm

# create prompt Template
def create_prompt_template():
    logger.info("Creating prompt template")
    prompt_template = """Use the following pieces of context to answer the question at the end. If you don't know the answer, just say that you don't know, don't try to make up an answer. 

    {context}

    Question: {question}
    Helpful Answer:"""
    PROMPT = PromptTemplate(
        template=prompt_template, input_variables=["context", "question"]
    )
    return PROMPT

# get response from LLM
def get_response(vectorstore, llm, prompt_template, query):
    logger.info("Getting response from LLM")
    chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vectorstore.as_retriever(search_type ="similarity", search_kwards={"k":3}),
        return_source_documents=True,
        chain_type_kwargs={"prompt": prompt_template}
    )
    result = chain.invoke(query)
    return result

def main():
    st.title("RAG with Amazon Titan and Bedrock")
    st.write("This app allows you to ask questions about your documents using Amazon Titan and Bedrock.")
    st.write("Upload your documents in the 'data' folder and click the 'Process Documents' button.")
    with st.sidebar:
        st.header("Settings")
        # Add any additional settings here
        if st.button("Process Documents"):
            if os.path.exists(f"githubbook.faiss"):
                st.write("Vector store already exists")
                vectorstore = FAISS.load_local(f"githubbook.faiss", bedrock_embeddings, allow_dangerous_deserialization=True)
            else:
                st.write("Processing documents")
                documents = load_documents_from_directory("data")
                texts = split_documents(documents)
                vectorstore = create_vector_store(texts)
                vectorstore.save_local(f"githubbook.faiss")
                st.write("Vector store saved successfully")
                #load the vector store
                vectorstore = FAISS.load_local(f"githubbook.faiss", bedrock_embeddings, allow_dangerous_deserialization=True)
                st.write("Vector store loaded successfully")
    llm = create_llm()
    prompt_template = create_prompt_template()
    st.write("You can now ask questions about your documents.")
    query = st.text_input("Enter your query:")
    if query:
        vectorstore = FAISS.load_local(f"githubbook.faiss", bedrock_embeddings, allow_dangerous_deserialization=True)
        logger.info("Vector store loaded!")
        result = get_response(vectorstore, llm, prompt_template, query)
        st.write(result["result"])

if __name__ == "__main__":
    main()
import os
import redis
from dotenv import load_dotenv
from redis.cluster import RedisCluster as MemoryDBCluster
from langchain_aws import ChatBedrock
from langchain_aws.embeddings import BedrockEmbeddings
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_aws.vectorstores.inmemorydb import InMemoryVectorStore
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
from langchain.chains import ConversationChain
import time 

load_dotenv()

#constants
INDEX_NAME = "rag-index"
PDF_FILE ="GitHub-book.pdf"
MEMORYDB_CLUSTER = os.getenv('MEMORYDB_CLUSTER')
print(f'DB Cluster: {MEMORYDB_CLUSTER}')
MEMORYDB_CLUSTER_URL = f"rediss://{MEMORYDB_CLUSTER}:6379/ssl=True&ssl_cert_reqs=none"
print(MEMORYDB_CLUSTER_URL)
#initialize the MemoryDB cluster endpoint
def init_memorydb_cluster():
    configs = get_configs()
    print(f"Connecting to MemoryDB cluster: {configs['MEMORYDB_CLUSTER']}")
    client = MemoryDBCluster(
        host=configs['MEMORYDB_CLUSTER'], 
        port=6379, 
        decode_responses=True,
        ssl_cert_reqs=None
    )
    try:
        client.ping()
        print("Successfully connected to MemoryDB cluster")
        return client
    except Exception as e:
        print("Error connecting to MemoryDB cluster: ", e)
        return None
    
  
# get the configuration
def get_configs():
    configs= {}
    configs['MEMORYDB_CLUSTER'] = os.getenv('MEMORYDB_CLUSTER')
    return configs

# Initialize the Bedrock LLM Model
def get_llm():
    #create Anthropic model
    model_kwargs ={
        "temperature":0,
        "top_k":250,
        "top_p":1,
        "stop_sequences":["\n\nHuman:"]
    }
    configs = get_configs()
    llm = ChatBedrock(model_id="anthropic.claude-3-sonnet-20240229-v1:0", model_kwargs=model_kwargs)
    return llm

# Initialize the Bedrock Embeddings Model
def get_embeddings():
    #create Bedrock embeddings model
    embeddings = BedrockEmbeddings()      
    return embeddings

# Check the index already exists in MemoryDB
def check_index_exists():
    #check if the index already exists
    try:
        redis_client = init_memorydb_cluster()
        info = redis_client.ft(INDEX_NAME).info()
        num_docs = info.get('num_docs', 'N/A')
        space_usage = info.get('space_usage', 'N/A')
        num_indexed_vectors = info.get('num_indexed_vectors', 'N/A')
        vector_space_usage = info.get('vector_space_usage', 'N/A')
        index_details = {
            'num_docs': num_docs,
            'space_usage': space_usage,
            'num_indexed_vectors': num_indexed_vectors,
            'vector_space_usage': vector_space_usage,
            'exists':True
        }        
        print("Index already exists")
        return index_details
    except Exception as e:
        print("Index does not exist")
        index_details = {
            'exists':False
        }
        return index_details
        

# initialize the VectorStore
def init_vector_store():
    #start measuring the exection time of the function
    start_time = time.time()
    embeddings =get_embeddings()
    try:
        # Step 1: Load and Split the Pdf. Initilize the pdfloader with the path
        loader = PyPDFLoader(file_path=PDF_FILE)
        #Load the Pdf pages
        pages = loader.load_and_split()
        # Step 2: Define the text splitter settings for chunking the text
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=100,
            separators=["\n\n", "\n", ".", " ", ""]           
        )
        # Step 3: Split the text into chunks
        chunks = loader.load_and_split(text_splitter=text_splitter)
    
        # Step 4: Create Memory DB vector Store
        #Initialize the MemoryDB With chunks and embedding details
        vector_store = InMemoryVectorStore.from_documents(
            documents=chunks,           
            index_name=INDEX_NAME,
            embeddings=embeddings,
            redis_url=MEMORYDB_CLUSTER_URL
        )
        # Step 5: Measure the execution time       
        end_time = time.time()
        print(f"--- Intialized vector Store--- {end_time - start_time:2f} seconds")
        # Step 5: Return the vector store
        return vector_store
    except Exception as e:
        print("Error initializing vector store: ", e)
        return None
    
  # initialize the retriever
def get_retriever(vector_store):
    """
    Initialize a redis instance as a retriever for an existing vector store

    :param redis_url: The URL of the Redis Instance
    :param index_name: The name of the index in the Redis vector store
    :param embeddings: The embeddings to use for the retriever
    :param index_schema: (Optional) The index schema, if needed
    :return: The retriever object or None in case of an error.
    """
    index_name=INDEX_NAME
    redis_url =MEMORYDB_CLUSTER_URL
    embeddings =get_embeddings()
    try:
        # Start measuring the execution time
        start_time = time.time()    
        #Step 1: Initialize the MemoryDB instance
        # memorydb_client = InMemoryVectorStore(
        #     index_name=index_name,
        #     embeddings=embeddings,
        #     redis_url=redis_url
        # )
        # Measure the initialization time
        end_time = time.time()
        print(f"--- Initialized MemoryDB client--- {end_time - start_time:2f} seconds")
        # start measure the execution time of the retriever creation
        start_time_retriever = time.time()
        # Step 2: Create the retriever from memoryDB instance
        retriever = memorydb_client.as_retriever()
        # Measure the execution time
        end_time_retriever = time.time()
        print(f"--- Created retriever--- {end_time_retriever - start_time_retriever:2f} seconds")
        return retriever
    except Exception as e:
        print("Error initializing retriever: ", e)
        return None

# Perform the query and return result from Memorydb client
def perform_query(query):
    results = memorydb_client.similarity_search(query)
    return results

#Initialize Retrieval QA with prompt
def query_and_get_response(question):
    system_prompt = ("You are a helpful assistant."
                     "You are given a question and a context. "
                     "Answer the question based on the context. "
                     "If the question cannot be answered using the information provided, say 'I don't know'"
                     "Context: {context}")
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            ("human", "{question}")
        ]
    )
    
    llm = get_llm()
    retriever = get_retriever()
    question_answer_chain = create_stuff_documents_chain(llm, prompt)
    chain = create_retrieval_chain(retriever, question_answer_chain)
    response = chain.invoke({"question": question})
    result= response["answer"]
    return result

def noContext(question):
    llm =get_llm()
    # construct a prompt that instructs the LLM to provide consise answers
    concise_prompt ="Please provide a concise answer to the following question:\n\n"
    # combine the consise ins with the user's question
    full_question = concise_prompt + question
    try:
        # invoke the LLM with the full question
        response = llm.invoke(full_question)
        result = response.content
        return result
    except Exception as e:
        print("Error invoking LLM: ", e)
        return None


memorydb_client = InMemoryVectorStore(
            index_name=INDEX_NAME,
            embedding=get_embeddings(),
            redis_url=MEMORYDB_CLUSTER_URL
            # index_schema=index_schema # Include the index schema if needed
        )
        
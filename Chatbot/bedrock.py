# import the necessary packages
import os
import boto3
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain.llms.bedrock import Bedrock
from langchain.prompts import PromptTemplate
import logging

# define logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)
logger.info("Logging Started")

def bedrock_chain():
    # create the Bedrock client
    bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')

    # create the Bedrock model
    llm = Bedrock(model_id="amazon.titan-text-lite-v1", client=bedrock)
    llm.model_kwargs = { "temperature": 0.5, "maxTokenCount": 512 }

    prompt_template =""" System: Following is the friendly conversation between knowledgable helpful assistant and a customer.
    The assistant is talkative and provides lots of specific details from its context
    Current Conversation:
    {history}

    User:{input}
    Bot:
    """
    # create the prompt
    prompt = PromptTemplate(
        input_variables=["history", "input"],
        template=prompt_template
    )

    # create the memory
    memory = ConversationBufferMemory(human_prefix="User", ai_prefix="Bot")

    # create the chain
    chain = ConversationChain(
        llm=llm,
        prompt=prompt,
        memory=memory
    )

    return chain

def run_chain(chain, prompt):
    # run the chain
    num_tokens = chain.llm.get_num_tokens(prompt)
    logger.info(f"Number of tokens: {num_tokens}")
    return chain({"input":prompt}), num_tokens

def clear_memory(chain):
    # clear the memory
    logger.info("Clearing memory")
    return chain.memory.clear()

import boto3
import os
import streamlit as st
from dotenv import load_dotenv
import datetime
load_dotenv()

#define file logging and configuration
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.info("Starting application")

#Environment variables
logger.info("Reading Environment Variable")
S3_BUCKET_NAME = os.getenv('S3_BUCKET_NAME')
S3_PREFIX = os.getenv('S3_PREFIX')

# Initialize the boto 3 client for S3
logger.info("Setting up boto3 client for s3")
#S3 = boto3.client('s3', aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'), aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'))
S3 = boto3.client('s3')

# process file and get filename
def process_file(file):
    logger.info(f"Original File info:{file}")
    try:
        name = file.name.split('.')[0]
        extension = file.name.split('.')[1]
        logger.info(datetime.datetime.now().strftime('%Y%m%d%H%M%S'))
        timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        file_name = f"{name}_{timestamp}.{extension}"
        logger.info(f'Rename File name: {file_name}')
        return file_name
    except Exception as e:
        logger.error(f'Error uploading file: {e}')

# method to upload file
def upload_file(file,renamed_file_name):
    try:
        S3.upload_fileobj(file, S3_BUCKET_NAME, renamed_file_name)
        logger.info('File uploaded successfully')
        return {"message":"File Uploaded successfully","status":True}
    except Exception as e:
        logger.error(f'Error uploading file: {e}')
        return {"message":f'Error uploading file: {e}',"status":False}

# S3 upload with prefix
def upload_file_with_prefix(file, renamed_file_name, prefix):
    try:
        S3.upload_fileobj(file, S3_BUCKET_NAME, f"{prefix}/{renamed_file_name}")
        logger.info('File uploaded successfully')
        return {"message":"File Uploaded successfully","status":True}
    except Exception as e:
        logger.error(f'Error uploading file: {e}')
        return {"message":f'Error uploading file: {e}',"status":False}

#Streamlit app
st.title('AWS S3 File Upload')
st.subheader('This is a simple application to upload files to S3',divider='rainbow')
st.write('Please choose a file to upload')
uploaded_file = st.file_uploader("Upload Document",type=['pdf'])
if uploaded_file is not None:
    try:
        modified_file_name = process_file(uploaded_file)
        #response = upload_file(uploaded_file, modified_file_name)
        response = upload_file_with_prefix(uploaded_file, modified_file_name, S3_PREFIX)
        if response['status']:
            st.success(response['message'])
        else:
            st.error(response['message'])
    except Exception as e:
        st.error(f'Error uploading file: {e}')


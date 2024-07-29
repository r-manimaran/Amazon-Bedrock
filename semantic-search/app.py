import search_lib
import logging
import streamlit as st

# define the logging
logging.basicConfig(level=logging.INFO, format='%(asctime)-15s %(levelname)s %(message)s')
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.info("Starting Semantic Search Demo")

st.set_page_config(
    page_title="Semantic Search",
    page_icon="���",
    layout="wide",
    initial_sidebar_state="expanded",
)
st.title("Semantic Search Demo")
# check if vector index is available in session state. if not load it.
if "vector_index" not in st.session_state:
    with st.spinner("Loading Vector Index..."):
        logger.info("Vector index not found in session state. Loading it")
        st.session_state.vector_index = search_lib.get_index()
        logger.info("Vector index loaded successfully")
        st.success("Vector index loaded successfully")

input_query = st.text_input("Enter your query about Amazon Bedrock", "What is Amazon Bedrock?")
submit_button = st.button("Search", type="primary")

if submit_button:
    with st.spinner("Searching..."):
        search_results = search_lib.get_similarity_search_results(st.session_state.vector_index, input_query)
        st.table(search_results)

                    
        
import streamlit as st
import pandas as pd
import rag_lib as glib

#streamlit app page configuration
st.set_page_config(
    page_title="Using MemoryDB as vectorDB",
    page_icon="���",
    layout="wide",
    initial_sidebar_state="expanded",
)
st.title("Using MemoryDB as vectorDB")

#initialize the memoryDB client
client = glib.init_memorydb_cluster()

#check if the index exists
index_exists = glib.check_index_exists()

if index_exists['exists']:
    st.write("Index already exists. You can ask questions")

    with st.form("question_form"):
        question = st.text_input("Ask your question here:")
        similarity_search =st.text_input("Similarity search:")
        submitted = st.form_submit_button("Submit")


        if submitted:
            if question:
                #No context question
                response = glib.noContext(question)

                #Retrieval-based Question
                retrieval_response = glib.get_retrieval_response(question)

                # Display responses side by side
                col1, col2 = st.columns(2)
                with col1:
                    st.subheader("No Context Response:")
                    st.write(response)
                with col2:
                    st.subheader("Response with Contexxt")
                    st.write(retrieval_response)

            if similarity_search:
                #similarity search
                similarity_response = glib.perform_query(similarity_search)

                # Create two columns for similarity search response and metadata
                col1, col2 = st.columns(2)
                with col1:
                    st.subheader("Similarity Search Response:")
                    for item in similarity_response: # Assuming similarity_response is iterable
                        st.write("Page Content:")
                        st.write(item.page_content)
                        st.text("")
                       
                with col2:
                    st.subheader("Metadata:")
                    for item in similarity_response:
                        st.write("Metadata:")
                        st.write(item.metadata)
                        st.text("")
else:
    st.write("Index does not exist. Please build the index first.")
    # Code to initialize the index
    vector_store = glib.init_vector_store()
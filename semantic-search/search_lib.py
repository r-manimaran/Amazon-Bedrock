from langchain_community.embeddings import BedrockEmbeddings
from langchain.indexes import VectorstoreIndexCreator
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.document_loaders.csv_loader import CSVLoader 

# Method to get Index after loading the csv file
def get_index():
    embeddings = BedrockEmbeddings()

    loader = CSVLoader(file_path="data/bedrock_faqs.csv")
    documents = loader.load()

    index_creator = VectorstoreIndexCreator(
        vectorstore_cls=FAISS,
        embedding= embeddings,
        text_splitter= CharacterTextSplitter(chunk_size=300,chunk_overlap =10)
    )
    index_from_loader = index_creator.from_loaders([loader])
    return index_from_loader

# method to perform Similarity Search based on input query in the input index
def get_similarity_search_results(index, query):
    similarity_search_results = index.vectorstore.similarity_search_with_score(query)
    flattened_results = [{"content":res[0].page_content, "score":res[1]} for res in similarity_search_results]
    return flattened_results
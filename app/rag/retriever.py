from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

from app.config import VECTOR_DB_DIR


def get_retriever():

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True}
    )

    vector_store = Chroma(
        persist_directory=str(VECTOR_DB_DIR),
        collection_name="aster_row_kb",
        embedding_function=embeddings
    )

    return vector_store.as_retriever(
        search_type="similarity",
        #search_kwargs={"k": 5}
        # search_kwargs={"k": 10}
        search_kwargs={"k": 15}
    )
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
import os

from langchain_text_splitters import RecursiveCharacterTextSplitter


def get_user_docs(user_id: str):
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    
    # Use collection_name to isolate each user's data
    os.makedirs(f"./chroma_db/{user_id}", exist_ok=True)
    db = Chroma(
        persist_directory=f"./chroma_db/{user_id}",
        embedding_function=embeddings
    )
    return db

def process_pdf(pdf_path, user_email):
    print("hereee - rag.py:21")
    loader = PyPDFLoader(pdf_path)
    documents = loader.load()

    # Split into chunks
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    documents = splitter.split_documents(documents)
    print("Splitted documents - rag.py:28", documents)

    for doc in documents:
        doc.metadata["source"] = os.path.basename(pdf_path)
        doc.metadata["user_email"] = user_email

    # # Create embeddings
    # embedding_function = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    # # Create user-specific directory for persistent storage
    # persist_directory = f"./chroma_db/{user_email}"
    # os.makedirs(persist_directory, exist_ok=True)

    # # Store embeddings persistently
    # vectordb = Chroma.from_documents(
    #     documents,
    #     embedding=embedding_function,
    #     persist_directory=persist_directory
    # )
    # vectordb.persist()

    # return vectordb
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
import os
from langchain_text_splitters import RecursiveCharacterTextSplitter
import requests
import json
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
def get_user_docs(user_id: str):
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    
    # Use collection_name to isolate each user's data
    persist_directory = f"./faiss_db/{user_id}"
    os.makedirs(persist_directory, exist_ok=True)

    # If you already have saved FAISS index, you can load it
    if os.path.exists(f"{persist_directory}/index.faiss"):
        db = FAISS.load_local(persist_directory, embeddings)
    else:
        db = FAISS(embedding_function=embeddings)
    
    return db

def load_vectorstore(user_id: str):
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    persist_directory = f"./faiss_db/{user_id}"
    if not os.path.exists(persist_directory):
        return None
    vectordb = FAISS.load_local(persist_directory, embeddings,  allow_dangerous_deserialization=True )
    return vectordb

def get_response(user_id: str, question: str, msg_history):
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
    
    # Headers
    headers = {
        "Content-Type": "application/json",
        "X-goog-api-key": api_key
    }
    vectordb = load_vectorstore(user_id)
    if vectordb is None:
        return "No documents found for this user."

    # Retrieve top 3 relevant docs
    retriever = vectordb.as_retriever(search_kwargs={"k": 3})
    docs = retriever.invoke(question)
    context = "\n".join([doc.page_content for doc in docs])

    # Build prompt for Gemini
    prompt = f"Given the context and past conversation history, only answer from the provided context. Give answers with proper explanation. Chat History: {msg_history}\nContext:\n{context}\n\nQuestion: {question}\nAnswer:"
    body = {
    "contents": [
        {
            "role": "user",
            "parts": [{"text": prompt}]
        }
    ]
    }

    # Make the POST request
    response = requests.post(url, headers=headers, data=json.dumps(body))
    data = response.json()

    answer =  data["candidates"][0]["content"]["parts"][0]["text"]
    return answer

def process_pdf(pdf_path, user_email):
    loader = PyPDFLoader(pdf_path)
    documents = loader.load()

    # Split into chunks
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    documents = splitter.split_documents(documents)

    # Add metadata
    for doc in documents:
        doc.metadata["source"] = os.path.basename(pdf_path)
        doc.metadata["user_email"] = user_email

    # Create embeddings
    embedding_function = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    # User-specific directory for persistent storage
    persist_directory = f"./faiss_db/{user_email}"
    os.makedirs(persist_directory, exist_ok=True)

    # If FAISS index already exists, load it; otherwise, create new
    index_path = os.path.join(persist_directory, "index.faiss")
    if os.path.exists(index_path):
        vectordb = FAISS.load_local(persist_directory, embedding_function,  allow_dangerous_deserialization=True )
        vectordb.add_documents(documents)
    else:
        vectordb = FAISS.from_documents(documents, embedding_function)
        vectordb.save_local(persist_directory)

    return vectordb



This project implements a **simple Retrieval-Augmented Generation (RAG) pipeline** using:

* **Google Gemini API** (Generative AI) for answering questions.
* **FAISS** for vector storage and similarity search.
* **HuggingFace Embeddings** (`sentence-transformers/all-MiniLM-L6-v2`) for document embeddings.
* **LangChain document loaders and text splitters** to process PDFs.

---

## Features

1. **User-specific FAISS storage**: Each user’s documents are stored in a separate FAISS index.
2. **PDF ingestion**: Split PDFs into chunks, embed them, and store in FAISS.
3. **Context-aware question answering**: Retrieves top relevant documents and asks Gemini API to answer **only from the retrieved context**.
4. **No SDK dependencies for Gemini**: The Gemini API is accessed via **direct HTTP requests** to avoid SDK version conflicts.

---

## Why Not Use the Gemini SDK?

The official Gemini SDK caused **version errors and compatibility issues** in the current environment. Instead of spending time resolving SDK-specific dependencies, I  used **direct REST API calls** to Gemini:

---

## Setup Instructions

1. **Clone the repository**

   ```bash
   git clone <repo-url>
   cd <repo-folder>
   ```

2. **Create a virtual environment and install dependencies**

   ```bash
   python -m venv venv
   source venv/bin/activate       # Linux/macOS
   venv\Scripts\activate          # Windows
   pip install -r requirements.txt
   ```

3. **Set up your environment variables**

   Create a `.env` file in the project root:

   ```
   GEMINI_API_KEY=YOUR_API_KEY
   ```

# API Reference

The `classic-rag` API provides endpoints for document ingestion, search, and health monitoring.

## Base URL
The default development server runs at `http://localhost:8000`.

## Endpoints

### 1. File Upload
`POST /upload`
Uploads a PDF or TXT file, extracts its text, chunks it, and ingests it into the vector store.
- **Form Data**:
  - `file`: The file to upload.
- **Response**:
  ```json
  {
    "status": "success",
    "filename": "document.pdf",
    "chunks_ingested": 15
  }
  ```

### 2. Chat (RAG)
`POST /chat`
The main RAG endpoint. It searches for relevant context and generates an answer using an LLM.
- **Request Body**:
  ```json
  {
    "message": "What is the remote work policy?"
  }
  ```
- **Response**:
  ```json
  {
    "answer": "The remote work policy allows for...",
    "sources": [
      {
        "id": "policy_v1_chunk_1",
        "content": "...",
        "metadata": { "source": "policy.pdf" }
      }
    ]
  }
  ```

### 3. Ingest Text
`POST /ingest-text`
Ingest raw text directly without uploading a file.
- **Request Body**:
  ```json
  {
    "text": "This is raw text to index.",
    "filename": "manual_entry.txt"
  }
  ```

### 4. Delete Documents
`DELETE /documents`
Removes specific document chunks from the vector store by their IDs.
- **Request Body**:
  ```json
  {
    "ids": ["id1", "id2"]
  }
  ```

### 5. Clear All Documents
`POST /documents/clear`
Clears the entire vector storage collection.

### 6. Health Check
`GET /health`
Returns the status of the API.
- **Response**: `{"status": "healthy"}`

## Static UI
The application includes a simple built-in UI accessible at:
`http://localhost:8000/static/index.html`

from fastapi import FastAPI, Depends, UploadFile, File
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from src.api.dependencies import get_rag_service
from src.core.rag_service import RAGService
from src.core.domain import LLMResponse, DocumentChunk
from src.api.middleware import LoggingMiddleware
from src.api.errors import setup_exception_handlers

app = FastAPI(title="Corporate Knowledge Base RAG API")

# Setup Middleware
app.add_middleware(LoggingMiddleware)

# Setup Exception Handlers
setup_exception_handlers(app)

# Mount Static Files (for UI)
app.mount("/static", StaticFiles(directory="src/api/static"), name="static")

@app.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    rag_service: RAGService = Depends(get_rag_service)
):
    """
    Upload a file (PDF/TXT), process it, and ingest into the vector store.
    """
    content = await file.read()
    num_chunks = await rag_service.process_file_upload(content, file.filename)
    return {"status": "success", "filename": file.filename, "chunks_ingested": num_chunks}

class ChatRequest(BaseModel):
    message: str = Field(..., example="What is the remote work policy?")

class IngestRequest(BaseModel):
    chunks: list[DocumentChunk]

class IngestTextRequest(BaseModel):
    text: str = Field(..., example="This is some raw text to index.")
    filename: str = Field(..., example="manual_input.txt")

@app.post("/ingest-text")
async def ingest_text(
    request: IngestTextRequest,
    rag_service: RAGService = Depends(get_rag_service)
):
    """
    Ingest raw text directly, chunking it and storing it.
    """
    num_chunks = await rag_service.process_file_upload(request.text.encode("utf-8"), request.filename)
    return {"status": "success", "filename": request.filename, "chunks_ingested": num_chunks}

@app.post("/ingest")
async def ingest(
    request: IngestRequest,
    rag_service: RAGService = Depends(get_rag_service)
):
    """
    Ingest a list of document chunks into the vector store.
    """
    await rag_service.ingest_documents(request.chunks)
    return {"status": "success", "message": f"Ingested {len(request.chunks)} chunks"}

class DeleteRequest(BaseModel):
    ids: list[str] = Field(..., example=["hr_policy_1"])

@app.delete("/documents")
async def delete_documents(
    request: DeleteRequest,
    rag_service: RAGService = Depends(get_rag_service)
):
    """
    Delete specific document chunks from the vector store.
    """
    await rag_service.delete_documents(request.ids)
    return {"status": "success", "message": f"Deleted {len(request.ids)} chunks"}

@app.post("/documents/clear")
async def clear_documents(
    rag_service: RAGService = Depends(get_rag_service)
):
    """
    Clear all documents from the vector store.
    """
    # For ChromaDB, we can delete by providing an empty filter or similar, 
    # but a simple way is just to delete all IDs or reset the collection.
    # In our implementation, we'll need to update the Port/Adapter.
    # For now, let's just implement a placeholder or a simple loop if we had IDs.
    # Actually, let's add reset support to the Port.
    await rag_service.clear_all_documents()
    return {"status": "success", "message": "All documents cleared"}

@app.post("/chat", response_model=LLMResponse)
async def chat(
    request: ChatRequest,
    rag_service: RAGService = Depends(get_rag_service)
):
    """
    Main RAG endpoint to ask questions against the knowledge base.
    """
    response = await rag_service.answer_query(request.message)
    return response

@app.get("/health")
async def health():
    return {"status": "healthy"}

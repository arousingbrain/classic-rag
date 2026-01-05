import pytest
from fastapi.testclient import TestClient
from src.api.main import app
from src.api.dependencies import get_rag_service
from src.core.domain import LLMResponse, DocumentChunk

@pytest.fixture
def client(rag_service):
    # Override the dependency to use the mocked rag_service
    app.dependency_overrides[get_rag_service] = lambda: rag_service
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()

def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_chat_endpoint(client, rag_service, mock_llm):
    mock_llm.generate_answer.return_value = "Mocked response"
    mock_llm.generate_embeddings.return_value = [0.1, 0.2]
    
    response = client.post("/chat", json={"message": "hello"})
    
    assert response.status_code == 200
    assert response.json()["answer"] == "Mocked response"

def test_upload_endpoint(client, rag_service, mock_doc_processor):
    mock_doc_processor.extract_text.return_value = "Extracted text"
    
    # Simulate file upload
    files = {"file": ("test.txt", b"file content", "text/plain")}
    response = client.post("/upload", files=files)
    
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert response.json()["chunks_ingested"] > 0

def test_ingest_endpoint(client, rag_service):
    data = {
        "chunks": [
            {
                "id": "test_1",
                "content": "test content",
                "metadata": {"source": "test"}
            }
        ]
    }
    response = client.post("/ingest", json=data)
    
    assert response.status_code == 200
    assert response.json()["status"] == "success"

def test_delete_endpoint(client, rag_service):
    response = client.request("DELETE", "/documents", json={"ids": ["test_1"]})
    
    assert response.status_code == 200
    assert response.json()["status"] == "success"

def test_clear_endpoint(client, rag_service):
    response = client.post("/documents/clear")
    
    assert response.status_code == 200
    assert response.json()["status"] == "success"

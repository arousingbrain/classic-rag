import pytest
from unittest.mock import MagicMock, patch
from src.core.domain import DocumentChunk, SearchResult, LLMResponse
from src.core.exceptions import ExternalServiceError

@pytest.mark.asyncio
async def test_chunk_text(rag_service):
    text = "A" * 2500
    chunks = rag_service._chunk_text(text, chunk_size=1000, overlap=200)
    
    # Expected chunks:
    # 1: 0-1000
    # 2: 800-1800
    # 3: 1600-2600 (stops at 2500)
    # 4: 2400-3400 (stops at 2500)
    assert len(chunks) == 4
    assert len(chunks[0]) == 1000
    assert len(chunks[3]) == 100

@pytest.mark.asyncio
async def test_process_file_upload(rag_service, mock_doc_processor, mock_llm, mock_storage):
    mock_doc_processor.extract_text.return_value = "This is a test document."
    mock_llm.generate_embeddings.return_value = [0.1, 0.2, 0.3]
    
    filename = "test.txt"
    file_content = b"fake content"
    
    count = await rag_service.process_file_upload(file_content, filename)
    
    assert count == 1
    mock_doc_processor.extract_text.assert_called_once()
    mock_llm.generate_embeddings.assert_called_once()
    mock_storage.upsert.assert_called_once()

@pytest.mark.asyncio
async def test_answer_query_success(rag_service, mock_llm, mock_storage):
    query_text = "What is the policy?"
    mock_llm.generate_embeddings.return_value = [0.1, 0.2]
    
    chunk = DocumentChunk(id="1", content="Policy details", metadata={"source": "test"})
    mock_storage.search.return_value = [SearchResult(chunk=chunk, score=0.9)]
    mock_llm.generate_answer.return_value = "The policy is X."
    
    response = await rag_service.answer_query(query_text)
    
    assert isinstance(response, LLMResponse)
    assert response.answer == "The policy is X."
    assert len(response.sources) == 1
    assert response.sources[0].content == "Policy details"

@pytest.mark.asyncio
async def test_answer_query_no_results(rag_service, mock_llm, mock_storage):
    mock_llm.generate_embeddings.return_value = [0.1]
    mock_storage.search.return_value = []
    mock_llm.generate_answer.return_value = "I don't know."
    
    response = await rag_service.answer_query("Unknown query")
    
    assert response.answer == "I don't know."
    assert len(response.sources) == 0

@pytest.mark.asyncio
async def test_answer_query_error(rag_service, mock_llm):
    mock_llm.generate_embeddings.side_effect = Exception("API Down")
    
    with pytest.raises(ExternalServiceError) as exc_info:
        await rag_service.answer_query("Fail")
    
    assert "Failed to process RAG query" in str(exc_info.value)
    assert "API Down" in str(exc_info.value.details["original_error"])

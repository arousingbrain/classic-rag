import pytest
import pytest_asyncio
from unittest.mock import MagicMock, AsyncMock
from src.core.rag_service import RAGService
from src.ports.storage import VectorStoragePort
from src.ports.llm import LLMPort
from src.ports.document_processor import DocumentProcessorPort

@pytest.fixture
def mock_storage():
    storage = MagicMock(spec=VectorStoragePort)
    storage.upsert = AsyncMock()
    storage.search = AsyncMock()
    storage.delete = AsyncMock()
    storage.clear_all = AsyncMock()
    return storage

@pytest.fixture
def mock_llm():
    llm = MagicMock(spec=LLMPort)
    llm.generate_answer = AsyncMock()
    llm.generate_embeddings = AsyncMock()
    return llm

@pytest.fixture
def mock_doc_processor():
    return MagicMock(spec=DocumentProcessorPort)

@pytest.fixture
def rag_service(mock_storage, mock_llm, mock_doc_processor):
    return RAGService(
        storage=mock_storage,
        llm=mock_llm,
        doc_processor=mock_doc_processor
    )

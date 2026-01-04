from functools import lru_cache
from fastapi import Depends
from src.config import Settings, settings
from src.ports.llm import LLMPort
from src.ports.storage import VectorStoragePort
from src.adapters.chroma_adapter import ChromaAdapter
from src.adapters.openai_adapter import OpenAIAdapter
from src.ports.document_processor import DocumentProcessorPort
from src.adapters.document_processor_adapter import LocalDocumentProcessor
from src.core.rag_service import RAGService

@lru_cache()
def get_settings() -> Settings:
    return settings

# Singletons for adapters
_llm_adapter: LLMPort = None
_storage_adapter: VectorStoragePort = None
_doc_processor: DocumentProcessorPort = None

def get_doc_processor() -> DocumentProcessorPort:
    global _doc_processor
    if _doc_processor is None:
        _doc_processor = LocalDocumentProcessor()
    return _doc_processor

def get_llm_port(settings: Settings = Depends(get_settings)) -> LLMPort:
    global _llm_adapter
    if _llm_adapter is None:
        _llm_adapter = OpenAIAdapter(settings)
    return _llm_adapter

def get_storage_port(settings: Settings = Depends(get_settings)) -> VectorStoragePort:
    global _storage_adapter
    if _storage_adapter is None:
        _storage_adapter = ChromaAdapter(settings)
    return _storage_adapter

def get_rag_service(
    llm: LLMPort = Depends(get_llm_port),
    storage: VectorStoragePort = Depends(get_storage_port),
    doc_processor: DocumentProcessorPort = Depends(get_doc_processor)
) -> RAGService:
    return RAGService(storage=storage, llm=llm, doc_processor=doc_processor)

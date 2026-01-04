import structlog
from typing import List
from src.core.domain import DocumentChunk, SearchQuery, LLMResponse, SearchResult
from src.ports.storage import VectorStoragePort
from src.ports.llm import LLMPort
from src.ports.document_processor import DocumentProcessorPort
from src.core.exceptions import ExternalServiceError
import uuid

logger = structlog.get_logger()

class RAGService:
    def __init__(self, storage: VectorStoragePort, llm: LLMPort, doc_processor: DocumentProcessorPort):
        self._storage = storage
        self._llm = llm
        self._doc_processor = doc_processor

    def _chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """Simple character-based chunking with overlap."""
        chunks = []
        start = 0
        while start < len(text):
            end = start + chunk_size
            chunks.append(text[start:end])
            start += chunk_size - overlap
        return chunks

    async def process_file_upload(self, file_content: bytes, filename: str) -> int:
        """Processes a file, chunks it, and ingests it."""
        logger.info("processing_file_upload", filename=filename)
        
        # 1. Extract text
        import io
        text = self._doc_processor.extract_text(io.BytesIO(file_content), filename)
        
        # 2. Chunk text
        text_chunks = self._chunk_text(text)
        
        # 3. Create DocumentChunk objects
        doc_chunks = [
            DocumentChunk(
                id=f"{filename}_{uuid.uuid4().hex[:8]}_{i}",
                content=chunk,
                metadata={"source": filename, "chunk_index": i}
            )
            for i, chunk in enumerate(text_chunks)
        ]
        
        # 4. Ingest
        await self.ingest_documents(doc_chunks)
        return len(doc_chunks)

    async def answer_query(self, query_text: str) -> LLMResponse:
        """
        Orchestrates the RAG flow:
        1. Embed the query.
        2. Search the storage for relevant context.
        3. Generate an answer based on the context.
        """
        logger.info("answering_query_started", query=query_text)
        
        try:
            # 1. Embed query
            logger.debug("generating_query_embedding")
            query_embedding = await self._llm.generate_embeddings(query_text)
            
            # 2. Search storage
            logger.debug("searching_vector_storage")
            search_query = SearchQuery(
                query=query_text, 
                embedding=query_embedding,
                top_k=5
            )
            search_results: List[SearchResult] = await self._storage.search(search_query)
            
            if not search_results:
                logger.warning("no_relevant_context_found", query=query_text)
            
            context_chunks = [res.chunk for res in search_results]
            
            # 3. Generate answer
            logger.debug("generating_final_answer")
            answer = await self._llm.generate_answer(query_text, context_chunks)
            
            logger.info("answering_query_completed", status="success")
            return LLMResponse(
                answer=answer,
                sources=context_chunks
            )
            
        except Exception as e:
            logger.error("rag_flow_failed", error=str(e))
            raise ExternalServiceError(
                message="Failed to process RAG query",
                details={"original_error": str(e)}
            ) from e

    async def ingest_documents(self, chunks: List[DocumentChunk]) -> None:
        """
        Ingest documents by generating embeddings and storing them.
        """
        logger.info("ingesting_documents_started", count=len(chunks))
        try:
            for chunk in chunks:
                if not chunk.embedding:
                    chunk.embedding = await self._llm.generate_embeddings(chunk.content)
            
            await self._storage.upsert(chunks)
            logger.info("ingesting_documents_completed", count=len(chunks))
        except Exception as e:
            logger.error("ingestion_failed", error=str(e))
            raise ExternalServiceError(
                message="Failed to ingest documents",
                details={"original_error": str(e)}
            ) from e

    async def delete_documents(self, ids: List[str]) -> None:
        """
        Delete specific document chunks from the vector store.
        """
        logger.info("deleting_documents_started", count=len(ids))
        try:
            await self._storage.delete(ids)
            logger.info("deleting_documents_completed", count=len(ids))
        except Exception as e:
            logger.error("deletion_failed", error=str(e))
            raise ExternalServiceError(
                message="Failed to delete documents",
                details={"original_error": str(e)}
            ) from e

    async def clear_all_documents(self) -> None:
        """
        Clear all documents from the vector store.
        """
        logger.info("clearing_all_documents_started")
        try:
            await self._storage.clear_all()
            logger.info("clearing_all_documents_completed")
        except Exception as e:
            logger.error("clearing_all_failed", error=str(e))
            raise ExternalServiceError(
                message="Failed to clear documents",
                details={"original_error": str(e)}
            ) from e

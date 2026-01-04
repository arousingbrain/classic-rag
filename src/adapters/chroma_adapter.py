from typing import List
import chromadb
from src.ports.storage import VectorStoragePort
from src.core.domain import DocumentChunk, SearchQuery, SearchResult
from src.config import Settings
import structlog

logger = structlog.get_logger()

class ChromaAdapter(VectorStoragePort):
    def __init__(self, settings: Settings):
        self._client = chromadb.PersistentClient(path=settings.CHROMA_PERSIST_DIRECTORY)
        self._collection = self._client.get_or_create_collection(name=settings.CHROMA_COLLECTION_NAME)

    async def upsert(self, chunks: List[DocumentChunk]) -> None:
        logger.info("upserting_to_chroma", count=len(chunks))
        
        ids = [chunk.id for chunk in chunks]
        documents = [chunk.content for chunk in chunks]
        metadatas = [chunk.metadata for chunk in chunks]
        # Chroma expects embeddings as a list of lists or None
        embeddings = [chunk.embedding for chunk in chunks]

        self._collection.upsert(
            ids=ids,
            documents=documents,
            metadatas=metadatas,
            embeddings=embeddings
        )

    async def search(self, query: SearchQuery) -> List[SearchResult]:
        logger.debug("searching_chroma", query=query.query)
        
        # We use the pre-calculated query embedding generated in rag_service.py
        if not query.embedding:
            # Fallback to text search if no embedding (Chroma will use its default embedding function)
            results = self._collection.query(
                query_texts=[query.query],
                n_results=query.top_k,
                where=query.filters
            )
        else:
            results = self._collection.query(
                query_embeddings=[query.embedding],
                n_results=query.top_k,
                where=query.filters
            )
        
        search_results = []
        # Chroma returns results in a nested list format
        if results and results["ids"]:
            for i in range(len(results["ids"][0])):
                chunk = DocumentChunk(
                    id=results["ids"][0][i],
                    content=results["documents"][0][i],
                    metadata=results["metadatas"][0][i]
                )
                search_results.append(SearchResult(chunk=chunk, score=results["distances"][0][i]))
            
        return search_results

    async def delete(self, ids: List[str]) -> None:
        logger.info("deleting_from_chroma", count=len(ids))
        self._collection.delete(ids=ids)

    async def clear_all(self) -> None:
        logger.info("clearing_entire_chroma_collection")
        # In Chroma, deleting by an empty 'where' or no 'ids' isn't supported for clearing all.
        # But we can just delete by IDs if we had them, OR just reset the collection.
        # A simple way is to get all IDs and then delete.
        results = self._collection.get()
        if results["ids"]:
            self._collection.delete(ids=results["ids"])

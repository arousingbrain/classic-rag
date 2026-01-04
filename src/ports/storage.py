from abc import ABC, abstractmethod
from typing import List
from src.core.domain import DocumentChunk, SearchQuery, SearchResult

class VectorStoragePort(ABC):
    @abstractmethod
    async def upsert(self, chunks: List[DocumentChunk]) -> None:
        """Store or update document chunks in the vector store."""
        pass

    @abstractmethod
    async def search(self, query: SearchQuery) -> List[SearchResult]:
        """Search for chunks similar to the query."""
        pass

    @abstractmethod
    async def delete(self, ids: List[str]) -> None:
        """Delete specific document chunks from the vector store."""
        pass

    @abstractmethod
    async def clear_all(self) -> None:
        """Removes all document chunks from the vector store."""
        pass

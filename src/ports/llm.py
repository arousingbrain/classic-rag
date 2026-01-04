from abc import ABC, abstractmethod
from typing import List
from src.core.domain import DocumentChunk

class LLMPort(ABC):
    @abstractmethod
    async def generate_answer(self, query: str, context_chunks: List[DocumentChunk]) -> str:
        """Generate an answer based on the provided query and context."""
        pass

    @abstractmethod
    async def generate_embeddings(self, text: str) -> List[float]:
        """Generate vector embeddings for the given text."""
        pass

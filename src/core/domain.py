from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class DocumentChunk(BaseModel):
    id: str = Field(..., description="Unique identifier for the chunk")
    content: str = Field(..., description="The text content of the chunk")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata for the document")
    embedding: Optional[List[float]] = Field(None, description="Vector embedding of the content")

class SearchQuery(BaseModel):
    query: str = Field(..., description="The user's natural language query")
    top_k: int = Field(default=5, description="Number of results to return")
    filters: Optional[Dict[str, Any]] = Field(None, description="Metadata filters for search")
    embedding: Optional[List[float]] = Field(None, description="Vector embedding of the query")

class SearchResult(BaseModel):
    chunk: DocumentChunk
    score: float = Field(..., description="Similarity score")

class LLMResponse(BaseModel):
    answer: str
    sources: List[DocumentChunk]

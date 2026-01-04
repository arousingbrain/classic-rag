from typing import List
import openai
from tenacity import retry, stop_after_attempt, wait_exponential

from src.ports.llm import LLMPort
from src.core.domain import DocumentChunk
from src.config import Settings
import structlog

logger = structlog.get_logger()

class OpenAIAdapter(LLMPort):
    def __init__(self, settings: Settings):
        self._client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self._model = settings.OPENAI_MODEL

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        reraise=True
    )
    async def generate_answer(self, query: str, context_chunks: List[DocumentChunk]) -> str:
        logger.debug("generating_answer_with_openai", model=self._model)
        
        context_text = "\n\n".join([f"Source {i+1}:\n{chunk.content}" for i, chunk in enumerate(context_chunks)])
        
        prompt = f"""You are a helpful corporate assistant. Use the following context to answer the user's question. 
        If the answer is not in the context, say you don't know based on the provided documents.
        
        Context:
        {context_text}
        
        Question: {query}
        Answer:"""
        
        response = await self._client.chat.completions.create(
            model=self._model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
        )
        return response.choices[0].message.content

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        reraise=True
    )
    async def generate_embeddings(self, text: str) -> List[float]:
        logger.debug("generating_embeddings_with_openai")
        response = await self._client.embeddings.create(
            input=[text],
            model="text-embedding-3-small"
        )
        return response.data[0].embedding

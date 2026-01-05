# Classic RAG

A professional-grade Retrieval-Augmented Generation (RAG) system built with scalability and maintainability in mind.

## Professional Implementation vs. Demo

Unlike a typical "first-timer" RAG demo, this project follows enterprise-grade practices like **Hexagonal Architecture**, **Dependency Injection**, and **Strict Domain Modeling**.

> [!TIP]
> **Curious about the internal design?** Check out the [Architecture Documentation](docs/architecture.md), [API Reference](docs/api.md), and [Development Guide](docs/development.md) in `/docs` for a deep dive.

## Features

- **File Ingestion**: Upload PDF or TXT files to process and store them in a vector database.
- **RAG-powered Chat**: Ask questions against your documents using OpenAI's LLMs.
- **Persistent Storage**: Uses ChromaDB for efficient vector search and storage.
- **Modern Architecture**: Built with Hexagonal Architecture (Ports and Adapters) for maintainability and testability.
- **Built-in UI**: A clean web interface for uploading files and chatting.

## Understanding RAG via this Project

This application is designed to be instructive. Here is how the three core components of RAG are implemented:

### 1. Chunking
Large documents must be broken into smaller "chunks" because LLMs have limited context windows and retrieval is more precise when focused on specific sections.

**Why it matters?**
If a chunk is too small, it loses its relationship with the rest of the text.
*   *Legal Example*: A sub-clause stating "this obligation is subject to Section 4.2" is useless if the chunk doesn't include (or can't find) Section 4.2.

In this project, we use a character-based chunking strategy with overlap:

```python
# From src/core/rag_service.py
def _chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
    """Simple character-based chunking with overlap."""
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks
```

**Why 1,000 characters?**
*   **Token Budget**: 1,000 chars is roughly 250-300 tokens. Retrieving the "Top 5" chunks stays well within the context window of modern LLMs.
*   **Semantic Density**: It's large enough to capture 1-3 paragraphs (a complete idea) but small enough to remain specific.
*   **Overlap (200 chars)**: Acts as "glue" to ensure sentences cut off at the end of one chunk are captured in full in the next.

#### Other Chunking Strategies
*   **Recursive Character Chunking**: Splits by a list of separators (paragraphs, then sentences, then words) to keep semantically related text together.
*   **Sentence Splitting**: Uses NLP libraries (like NLTK or SpaCy) to ensure chunks never break in the middle of a sentence.
*   **Semantic Chunking**: Uses embeddings to find natural "breaks" in the meaning of the text, creating chunks of varying sizes based on content.

### 2. Embeddings
Computers can't "read" text like humans; they process numbers. We convert text into high-dimensional vectors (embeddings) where similar meanings are close together in vector space.

**Why it matters?**
Embeddings turn abstract concepts into measurable distances.
*   *Legal Example*: The system doesn't need to know the definition of "Force Majeure"; it just knows that the vector for that term is mathematically close to "Act of God" or "unforeseeable circumstances."

We use OpenAI's `text-embedding-3-small` model for this:

```python
# From src/adapters/openai_adapter.py
async def generate_embeddings(self, text: str) -> List[float]:
    response = await self._client.embeddings.create(
        input=[text],
        model="text-embedding-3-small"
    )
    return response.data[0].embedding
```

#### Other Embedding Strategies
*   **Local Models (Open Source)**: Using models like `all-MiniLM-L6-v2` via HuggingFace. This is cheaper and keeps data private (on-premise).
*   **Domain-Specific Models**: Using models fine-tuned on legal or medical databases for higher precision in those specific fields.
*   **Custom Fine-Tuning**: Training an embedding model on your own specific company data to understand internal acronyms and projects.

### 3. Retrieval
Retrieval is the search for the most relevant chunks in our vector database when a user asks a question.

#### The Strategy: Semantic Search
Unlike a keyword search (which looks for exact word matches), this project uses **Semantic Search**. It finds documents based on *meaning* and *context* by comparing their vector positions.

**Why use this?**
*   **Conceptual Matching**: It can find relevant information even if the user uses different words than the document.
    *   *Legal Example*: If a user searches for "employment termination," the system will find clauses about "employee separation" or "dismissal for cause" because they are semantically related.
*   **Handling Ambiguity**: It understands nuances that keywords miss. A keyword search for "suit" might return "lawsuit" and "formal attire" interchangeably, but a vector embedding captures the surrounding legal context to prioritize the legal meaning.

**Technical Details:**

1.  **Similarity Metric**: We use **Cosine Similarity** to measure the angle between the query vector and document vectors. The smaller the angle, the more similar the content.
2.  **Indexing Algorithm**: ChromaDB uses **HNSW (Hierarchical Navigable Small Worlds)**. This builds a graph of vectors, allowing the system to find the "nearest neighbors" in milliseconds, even with millions of documents ($O(\log n)$ speed).

#### Implementation
First, we search ChromaDB for the closest vectors:

```python
# From src/adapters/chroma_adapter.py
async def search(self, query: SearchQuery) -> List[SearchResult]:
    # Chroma returns results based on cosine similarity of embeddings
    results = self._collection.query(
        query_embeddings=[query.embedding],
        n_results=query.top_k,
        where=query.filters
    )
    # ... formatting results ...
```

Then, the `RAGService` orchestrates the flow:

```python
# From src/core/rag_service.py
async def answer_query(self, query_text: str) -> LLMResponse:
    # 1. Embed query (Convert text to vector)
    query_embedding = await self._llm.generate_embeddings(query_text)
    
    # 2. Search storage (Find relevant context)
    search_results = await self._storage.search(SearchQuery(query_text, query_embedding))
    
    # 3. Generate answer (Ask LLM with context)
    context_chunks = [res.chunk for res in search_results]
    answer = await self._llm.generate_answer(query_text, context_chunks)
    return LLMResponse(answer=answer, sources=context_chunks)
```

#### Other Strategies
While Vector Search is the core of this project, production RAG systems often use additional strategies. 

> [!NOTE]
> To illustrate these concepts consistently, we use **Legal Intelligence** as a mental model below. However, this application is domain-agnostic and can be used for any field (Medical, Technical, HR, etc.).

*   **Keyword Search (BM25)**: Useful for finding exact statute IDs, case citations, or rare legal jargon that embeddings might miss.
    *   *Legal Example*: Searching for a specific statute number like "18 U.S.C. § 1343" (Wire Fraud).
*   **Hybrid Search**: Combines Keyword and Vector search (using *Reciprocal Rank Fusion*) to find both specific identifiers and broad legal concepts.
    *   *Legal Example*: Searching for the concept of "duty of care" while ensuring results specifically mention "medical malpractice."
*   **Reranking**: A two-stage process where you retrieve many possible precedents quickly, then use a "cross-encoder" model to score the most relevant ones.
    *   *Legal Example*: High-stakes precedent research where the single most relevant case must be at the very top.
*   **Metadata Filtering**: Applying hard constraints (e.g., limiting search to specific courts or years) before performing the similarity search.
    *   *Legal Example*: Restricting a search for "privacy laws" to only include documents from the "California" jurisdiction.
*   **Parent-Document Retrieval**: Searching small extracted clauses for precision, but retrieving the entire "parent" section or article to provide the LLM with full context.
    *   *Legal Example*: Finding a specific sub-clause in a 100-page contract, but pulling the entire "Definitions" section to interpret it.

## Tech Stack

- **Framework**: FastAPI
- **Vector DB**: ChromaDB
- **LLM**: OpenAI (GPT-4o or similar)
- **Logging**: structlog
- **Dependency Management**: uv

## Getting Started

1.  **Environment Setup**:
    Create a `.env` file with your OpenAI API key:
    ```env
    OPENAI_API_KEY=your_key_here
    ```

2.  **Install Dependencies**:
    ```bash
    uv sync
    ```

3.  **Run the App**:
    ```bash
    uv run python main.py
    ```

4.  **Running Tests**:
    Verify the installation by running the test suite:
    ```bash
    PYTHONPATH=. uv run pytest
    ```

Access the UI at `http://localhost:8000/static/index.html`.

## Project Structure

- `docs/`: Detailed design, [Architecture](docs/architecture.md), [API Reference](docs/api.md), and [Development Guide](docs/development.md).
- `src/api/`: FastAPI application and static UI files.
- `src/core/`: Domain logic and RAG service orchestration.
- `src/ports/`: Interface definitions for storage, LLM, and document processing.
- `src/adapters/`: Concrete implementations (ChromaDB, OpenAI, etc.).

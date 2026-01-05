# Master RAG with Classic RAG: A Learning Guide

This guide provides a structured path to learning Retrieval-Augmented Generation (RAG) by exploring the `classic-rag` codebase. Instead of just reading, you will trace code, run experiments, and modify the system to see how it reacts.

---

## 🏗️ Phase 1: The Blueprint (Architecture)

Before diving into lines of code, understand the software design. Modern RAG systems require clean boundaries between the "intelligence" (LLM) and the "data" (Vector DB).

1.  **Read**: [System Architecture](docs/architecture.md)
2.  **Code Walkthrough**: Open `src/ports/`. Note how `VectorStoragePort` and `LLMPort` are just interfaces.
3.  **The Connector**: Look at `src/adapters/`. See how `ChromaAdapter` implements the storage port and `OpenAIAdapter` implements the LLM port.
4.  **Experiment**: Open `src/api/dependencies.py`. This is where the choices are made. Imagine swapping `OpenAIAdapter` for a `MockLLMAdapter` for testing.

---

## 📥 Phase 2: The Ingestion Pipeline (Preparation)

RAG is only as good as the data it consumes. This phase covers how documents become searchable vectors.

### 1. The Processing Flow
Trace a file upload:
- `src/api/main.py` (the endpoint) ⮕ `RAGService.ingest_document` in `src/core/rag_service.py`

### 2. Chunking Logic
Open `src/core/rag_service.py` and find `_chunk_text`.
- **Question**: Why do we use `overlap`? What happens if you set it to 0?
- **Experiment**: Change `chunk_size` from 1000 to 100 in `src/core/rag_service.py` (line 35). Upload a large document and see how many chunks are created in the logs.

### 3. Creating Embeddings
Open `src/adapters/openai_adapter.py`.
- Look at `generate_embeddings`. Notice we use `text-embedding-3-small`.
- Research: What is the dimensionality of this model? (Hint: check OpenAI docs).

---

## 🔍 Phase 3: The Retrieval Loop (Search)

Now that data is stored, how do we find it?

### 1. Vector Search
Trace a query:
- `RAGService.answer_query` in `src/core/rag_service.py` ⮕ `ChromaAdapter.search` in `src/adapters/chroma_adapter.py`.

### 2. Similarity Metric
In `ChromaAdapter`, note that we don't explicitly calculate similarity—Chroma does it for us.
- **Deep Dive**: Research "Cosine Similarity" vs "Euclidean Distance". Which one is Chroma using by default?

---

## ✍️ Phase 4: Synthesis & Generation (The "G" in RAG)

This is where the retrieved context is combined with the user's question.

1.  **The Prompt**: Open `src/adapters/openai_adapter.py` and look at `generate_answer`.
2.  **Instruction**: Note the system prompt. How does it instruct the LLM to use the context? 
3.  **Experiment**: Modify the prompt in `generate_answer` to make the LLM respond only in a specific style (e.g., "Respond like a pirate"). Observe how the retrieved facts stay the same, but the delivery changes.

---

## 🛠️ Phase 5: Hands-On Challenges

To truly master RAG, you must build upon the foundation.

1.  **Level 1: Metadata Enhancement**: Modify `_chunk_text` to include the filename in every chunk so the LLM knows which document it's reading from.
2.  **Level 2: Reranking**: (Advanced) Add a new service that takes the Top 5 results from Chroma and uses a cheaper LLM call to pick the Top 2 most relevant ones before passing them to the final generation step.
3.  **Level 3: Multi-format support**: Try adding an adapter for `.docx` or `.html` files in `src/adapters/local_document_processor.py`.

---

## 🛡️ Phase 6: Resilience & Reliability (The "Professional" Touch)

This project isn't just about RAG; it's about *reliable* RAG.

1.  **Reactive Resilience**: Open `src/adapters/openai_adapter.py`. 
    - Find the `@retry` decorator. 
    - **Question**: Why do we use it? How does it handle a `RateLimitError`?
2.  **Structured Observability**: Run the app and look at the terminal output.
    - Notice every log has a `request_id`.
    - Trace where this originates in `src/api/middleware.py`.
3.  **Domain Exceptions**: Look at `src/core/exceptions.py`.
    - See how we wrap generic errors into domain-specific ones. This prevents "leaky abstractions" where the API has to know about database internals.

---

## ✅ Phase 7: Prove It Works

Finally, learn how to verify a non-deterministic system.

1.  **Unit Tests**: Run `PYTHONPATH=. uv run pytest tests/unit/test_rag_service.py`.
2.  **Integration Tests**: Run `PYTHONPATH=. uv run python verify_rag.py`.
3.  **UI Testing**: Open the web interface, upload a document, and verify the reference "sources" in the UI match the document content.

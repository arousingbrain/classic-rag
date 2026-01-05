# System Architecture

The `classic-rag` application is built with a focus on maintainability, testability, and decoupling. It follows the **Hexagonal Architecture** (also known as Ports and Adapters) pattern and uses **Dependency Injection** as its core orchestration mechanism.

## Architectural Design: Hexagonal Architecture

Hexagonal architecture isolation means the business logic (the "Core") is separated from external concerns like databases, LLMs, and APIs.

### 1. The Core (Domain & Services)
- **Domain**: Located in `src/core/domain.py`, it contains the pure data models (e.g., `DocumentChunk`, `SearchQuery`, `LLMResponse`).
- **Services**: Located in `src/core/rag_service.py`, it contains the orchestration logic for the RAG flow. It only interacts with "Ports," never concrete implementations.

### 2. Ports (Interfaces)
Ports are abstract base classes (interfaces) that define the "contract" for external interactions. They are located in `src/ports/`.
- `VectorStoragePort`: Interface for storing and searching vectors.
- `LLMPort`: Interface for generating embeddings and answers.
- `DocumentProcessorPort`: Interface for extracting text from various file formats.

### 3. Adapters (Implementations)
Adapters are the concrete implementations of the Ports, located in `src/adapters/`.
- `ChromaAdapter`: Implementation of `VectorStoragePort` using ChromaDB.
- `OpenAIAdapter`: Implementation of `LLMPort` using OpenAI's API.
- `LocalDocumentProcessor`: Implementation of `DocumentProcessorPort` for PDF and TXT processing.

---

## Dependency Injection (DI)

Dependency Injection is used to wire everything together. This ensures that the `RAGService` doesn't know *which* database or LLM it's using, only that they follow the required interface.

### Constructor Injection
The `RAGService` receives its dependencies through its constructor:
```python
class RAGService:
    def __init__(self, storage: VectorStoragePort, llm: LLMPort, doc_processor: DocumentProcessorPort):
        self._storage = storage
        self._llm = llm
        self._doc_processor = doc_processor
```

### Composition Root (FastAPI Depends)
The `src/api/dependencies.py` file acts as the "Composition Root." It uses FastAPI's `Depends` system to handle the lifecycle and injection of these components.

```python
# Example from src/api/dependencies.py
def get_rag_service(
    llm: LLMPort = Depends(get_llm_port),
    storage: VectorStoragePort = Depends(get_storage_port),
    doc_processor: DocumentProcessorPort = Depends(get_doc_processor)
) -> RAGService:
    return RAGService(storage=storage, llm=llm, doc_processor=doc_processor)
```

### Benefits
- **Testability**: We can easily replace real adapters with mocks for unit testing the core logic.
- **Flexibility**: Swapping out ChromaDB for Pinecone or OpenAI for Anthropic only requires writing a new Adapter—the Core logic remains unchanged.
- **Clean Code**: Dependencies are explicit, making the system easier to reason about.

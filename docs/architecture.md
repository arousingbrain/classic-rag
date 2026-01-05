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

---

## Resiliency & Error Handling

The application is designed for enterprise-grade reliability, focusing on structured observability and failure recovery.

### 1. Reactive Resilience (Retries)
Instead of proactive "connectivity pings," the application uses a reactive pattern for external services (e.g., OpenAI).
- **Mechanism**: We use the `tenacity` library to wrap external calls with **exponential backoff retries**.
- **Rationale**: This handles transient network issues and rate limiting gracefully without failing the user request immediately.
- **Example**: See `src/adapters/openai_adapter.py`.

### 2. Exception Wrapping & Isolation
To prevent implementation details from leaking and to keep the Core decoupled:
- **Core Exceptions**: Domain-specific exceptions are defined in `src/core/exceptions.py` (e.g., `ExternalServiceError`).
- **Isolation**: Adapters and services wrap low-level errors (like `openai.RateLimitError`) into these Core exceptions. This ensures the API layer only needs to know about the domain's error language, not the specifics of every vendor.

### 3. Centralized Global Error Mapping
All exceptions are handled at the edge of the system:
- **FastAPI Exception Handlers**: In `src/api/errors.py`, we map `AppException` and its subclasses to structured JSON responses.
- **Security**: A catch-all handler for the generic `Exception` class ensures that unexpected internal tracebacks are logged but never returned to the client.

### 4. Structured Observability
- **Contextual Logging**: Every request is assigned a unique `X-Request-ID` in `src/api/middleware.py`.
- **Traceability**: All logs (info, warning, error) are tagged with this ID, allowing developers to trace a single request's journey through the various layers of the architecture.

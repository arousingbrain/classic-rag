# Development Guide

This guide covers how to set up the development environment, run tests, and contribute to `classic-rag`.

## Environment Setup

### 1. Prerequisites
- **Python**: 3.13 or higher.
- **uv**: We use `uv` for dependency management. [Install uv](https://github.com/astral-sh/uv).

### 2. Initialization
```bash
# Clone the repository
git clone <repo-url>
cd classic-rag

# Install dependencies and create a virtual environment
uv sync
```

### 3. Configuration
Create a `.env` file in the root directory:
```env
OPENAI_API_KEY=your_openai_api_key
CHROMA_PERSIST_DIRECTORY=./chroma_data
CHROMA_COLLECTION_NAME=rag_collection
```

## Running the Application

### Start the API
```bash
uv run python main.py
```
The API will be available at `http://localhost:8000`.

### Development with Auto-reload
For faster development, you can use `uvicorn` directly:
```bash
uv run uvicorn src.api.main:app --reload
```

## Verification & Testing

### Verification Script
We have a handy script to verify the RAG flow:
```bash
uv run python verify_rag.py
```

### Future testing
Unit tests are located in `tests/` (to be implemented). You can run them using:
```bash
uv run pytest
```

## Contributing

1.  **Code Style**: We follow standard Python PEP 8 guidelines.
2.  **Hexagonal Architecture**: Ensure all new business logic is placed in `src/core` and stays implementation-agnostic. Define any new external dependencies as **Ports** in `src/ports`.
3.  **Dependency Injection**: Use the existing patterns in `src/api/dependencies.py` to wire new components.

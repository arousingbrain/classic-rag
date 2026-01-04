# Classic RAG

A professional-grade Retrieval-Augmented Generation (RAG) system built with scalability and maintainability in mind.

## Professional Implementation vs. Demo

Unlike a typical "first-timer" RAG (which often bundles all logic inside a single Jupyter notebook or FastAPI route), this project follows enterprise-grade practices:

- **Hexagonal Architecture**: Business logic is isolated in the `core` layer, protected by **Ports** (interfaces). Concrete **Adapters** (OpenAI, ChromaDB) are injected at runtime, making the system 100% swappable and testable.
- **Dependency Injection**: Services are not hardcoded; they are managed through a proper DI layer, ensuring clean lifecycle management and easy mocking for tests.
- **Production-Ready Observability**: Uses `structlog` for machine-readable logging and custom middleware to track API health and performance metrics.
- **Strict Domain Modeling**: Core domain objects (`DocumentChunk`, `LLMResponse`) ensure type safety across the entire pipeline, preventing the "blind dictionary passing" common in a basic demo codebases.
- **Modern Tooling**: Managed by `uv` for lightning-fast, reproducible builds and deterministic dependency resolution.

## Features

- **File Ingestion**: Upload PDF or TXT files to process and store them in a vector database.
- **RAG-powered Chat**: Ask questions against your documents using OpenAI's LLMs.
- **Persistent Storage**: Uses ChromaDB for efficient vector search and storage.
- **Modern Architecture**: Built with Hexagonal Architecture (Ports and Adapters) for maintainability and testability.
- **Built-in UI**: A clean web interface for uploading files and chatting.

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
    Access the UI at `http://localhost:8000/static/index.html`.

## Project Structure

- `src/api`: FastAPI application and static UI files.
- `src/core`: Domain logic and RAG service orchestration.
- `src/ports`: Interface definitions for storage, LLM, and document processing.
- `src/adapters`: Concrete implementations (ChromaDB, OpenAI, etc.).

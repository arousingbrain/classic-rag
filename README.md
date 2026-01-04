# Classic RAG

A Retrieval-Augmented Generation (RAG) system with a FastAPI backend and a built-in UI for querying a knowledge base.

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

# Corrective RAG Project

A **Corrective Retrieval-Augmented Generation (CRAG)** system with self-correction mechanisms, relevance evaluation, and web search fallback.

## Installation

```bash
# Install dependencies
uv sync

# Set OpenAI API key
export OPENAI_API_KEY='your-api-key-here'
```

## Quick Start

### 1. Add Documents

```bash
uv run python cli.py add-directory examples/sample_documents
```

### 2. Run Web Demo

```bash
uv run streamlit run demo.py
```

### 3. Use CLI

```bash
# Simple query
uv run python cli.py query "Your question here"

# Query with diagnostics
uv run python cli.py query "Your question here" --diagnostics

# Interactive mode
uv run python cli.py interactive
```

### 4. REST API

```bash
# Start server
uv run python main.py

# API will run at http://localhost:8000
# View docs at http://localhost:8000/docs
```

## Project Structure

```
rag-project/
├── src/
│   ├── rag_system.py              # Traditional RAG
│   ├── corrective_rag_system.py    # Corrective RAG
│   └── api.py                     # FastAPI REST API
├── examples/
│   └── sample_documents/          # Sample documents
├── demo.py                        # Streamlit web demo
├── cli.py                         # CLI interface
└── main.py                        # FastAPI server
```

## Configuration

Parameters that can be adjusted in `CorrectiveRAGSystem`:

- `relevance_threshold`: Relevance threshold (default: 0.7)
- `use_web_search`: Enable/disable web search fallback (default: True)
- `retriever_k`: Number of documents to retrieve (default: 4)
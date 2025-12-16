# Corrective RAG Project

A complete **Corrective Retrieval-Augmented Generation (CRAG)** system built with LangChain, ChromaDB, and FastAPI. This system goes beyond traditional RAG by implementing self-correction mechanisms that evaluate document relevance and use web search as a fallback.

## What is Corrective RAG?

Corrective RAG (CRAG) is an advanced RAG technique that improves answer quality through:

1. **Relevance Grading**: Automatically evaluates whether retrieved documents are relevant to the query
2. **Self-Correction**: Filters out irrelevant documents before generating answers
3. **Web Search Fallback**: Automatically searches the web when local documents are insufficient
4. **Adaptive Response**: Combines multiple information sources intelligently

### How It Works

```
User Query → Retrieve Documents → Grade Relevance → Self-Correction → Generate Answer
                                         ↓
                                   Low Relevance?
                                         ↓
                                   Web Search → Additional Context
```

## Features

- **🔍 Intelligent Document Retrieval**: Vector-based semantic search using ChromaDB
- **✅ Relevance Grading**: LLM-powered evaluation of document relevance
- **🌐 Web Search Fallback**: Automatic web search when local documents aren't sufficient
- **🎯 Self-Correction**: Filters irrelevant information before generating answers
- **📊 Diagnostic Mode**: Detailed insights into the correction process
- **🚀 REST API**: Complete FastAPI-based REST API
- **💻 CLI Interface**: Rich command-line interface with diagnostics
- **🔧 Configurable**: Adjustable relevance thresholds and search settings

## Installation

This project uses `uv` for dependency management. Make sure you have `uv` installed.

```bash
# Clone or navigate to the project directory
cd rag-project

# Install dependencies
uv sync
```

## Configuration

1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Edit `.env` and add your OpenAI API key:
```bash
OPENAI_API_KEY=your_openai_api_key_here
```

**Important**: OpenAI API key is required for:
- Document embeddings (using `text-embedding-3-large`)
- Relevance grading (using GPT models)
- Answer generation (using GPT models)

For detailed information about OpenAI embeddings, see [OPENAI_EMBEDDINGS.md](OPENAI_EMBEDDINGS.md).

## Quick Start

### 1. Add Documents

```bash
# Add documents from a directory
uv run python cli.py add-directory examples/sample_documents

# Check status
uv run python cli.py status
```

### 2. Query with Corrective RAG

```bash
# Simple query
uv run python cli.py query "What is Python?"

# Query with diagnostics to see the correction process
uv run python cli.py query "What is Python?" --diagnostics

# Interactive mode
uv run python cli.py interactive
```

## Usage

### 1. REST API

Start the FastAPI server:

```bash
# Using uv
uv run python main.py

# Or activate the virtual environment first
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
python main.py
```

The API will be available at `http://localhost:8000`

API Documentation: `http://localhost:8000/docs`

#### API Endpoints

- `GET /` - API information
- `GET /status` - System status including CRAG configuration
- `POST /upload/files` - Upload files
- `POST /upload/directory` - Process directory
- `POST /query` - Ask questions (supports diagnostics)
  ```json
  {
    "question": "What is Python?",
    "k": 4,
    "return_diagnostics": true
  }
  ```
- `POST /search` - Similarity search
- `DELETE /reset` - Reset vector store

#### Example API Usage

```bash
# Start the server
uv run python main.py

# Query with diagnostics
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is machine learning?",
    "k": 4,
    "return_diagnostics": true
  }'
```

### 2. Command Line Interface

```bash
# Using uv
uv run python cli.py --help
```

#### CLI Commands

```bash
# Check system status (shows CRAG configuration)
uv run python cli.py status

# Add documents from directory
uv run python cli.py add-directory /path/to/documents

# Add specific files
uv run python cli.py add-files file1.txt file2.txt

# Query with basic output
uv run python cli.py query "What is the main topic?"

# Query with diagnostics (see relevance grading, web search usage)
uv run python cli.py query "What is quantum computing?" --diagnostics

# Search for similar documents
uv run python cli.py search "search query"

# Analyze document chunks and embeddings
uv run python cli.py analyze-chunks examples/sample_documents/python_intro.txt

# Interactive mode (shows quick diagnostics for each query)
uv run python cli.py interactive

# Reset vector store
uv run python cli.py reset
```

### 3. Python API

```python
from src.corrective_rag_system import CorrectiveRAGSystem

# Initialize the system with custom settings
rag = CorrectiveRAGSystem(
    openai_api_key="your-api-key",
    relevance_threshold=0.6,  # 60% relevance threshold
    use_web_search=True
)

# Load existing vector store or create new one
rag.load_vectorstore()

# Add documents
documents = rag.load_documents_from_directory("./documents")
rag.add_documents(documents)

# Query with diagnostics
result = rag.query(
    "What is the main topic of the documents?",
    k=4,
    return_diagnostics=True
)

# Access results
print(result["answer"])

# View diagnostics
if "diagnostics" in result:
    diag = result["diagnostics"]
    print(f"Retrieved: {diag['total_retrieved']}")
    print(f"Relevant: {diag['relevant_count']}")
    print(f"Relevance Ratio: {diag['relevance_ratio']:.2%}")
    print(f"Used Web Search: {diag['used_web_search']}")

# Search for similar documents
docs = rag.similarity_search("search query", k=5)
```

## Project Structure

```
rag-project/
├── src/
│   ├── __init__.py
│   ├── corrective_rag_system.py  # Core Corrective RAG implementation
│   ├── rag_system.py             # Original RAG system (kept for reference)
│   ├── api.py                    # FastAPI application
│   └── cli.py                    # Command line interface
├── examples/
│   └── sample_documents/         # Sample documents for testing
├── main.py                       # API server entry point
├── cli.py                        # CLI entry point
├── pyproject.toml                # Project configuration
├── .env.example                  # Environment variables template
├── README.md                     # This file
└── chroma_db/                    # Vector database (created automatically)
```

## Corrective RAG Configuration

The system can be configured with various parameters:

```python
CorrectiveRAGSystem(
    openai_api_key="your-api-key",
    embedding_model="text-embedding-3-large",  # Embedding model
    llm_model="gpt-3.5-turbo",                # LLM for grading and generation
    chunk_size=1000,                          # Document chunk size
    chunk_overlap=200,                        # Chunk overlap
    persist_directory="./chroma_db",          # Vector store location
    relevance_threshold=0.6,                  # Relevance threshold (0-1)
    use_web_search=True                       # Enable web search fallback
)
```

### Relevance Threshold

- **High (0.8-1.0)**: Strict - will use web search more often
- **Medium (0.5-0.7)**: Balanced - good for most use cases
- **Low (0.0-0.4)**: Lenient - relies more on local documents

## Understanding Diagnostics

When using `return_diagnostics=True`, you get detailed information:

```json
{
  "total_retrieved": 4,
  "relevant_count": 2,
  "irrelevant_count": 2,
  "relevance_ratio": 0.5,
  "used_web_search": true,
  "web_search_results": "...",
  "grading_results": [
    {
      "content_preview": "...",
      "is_relevant": true,
      "grade_response": "{\"score\": \"yes\"}"
    }
  ]
}
```

## Dependencies

- **LangChain**: Framework for building LLM applications
- **ChromaDB**: Vector database for embeddings
- **OpenAI**: GPT models and embedding models
- **DuckDuckGo Search**: Web search fallback
- **FastAPI**: Modern web framework for APIs
- **Typer**: CLI framework
- **Rich**: Beautiful terminal output

## Examples

### Example 1: Query with Self-Correction

```bash
# The system will:
# 1. Retrieve documents about Python
# 2. Grade their relevance
# 3. Filter irrelevant ones
# 4. Use web search if needed
# 5. Generate answer from corrected context

uv run python cli.py query "What is Python programming?" --diagnostics
```

### Example 2: Comparing Documents

```bash
# Add documents
mkdir documents
echo "Python is a high-level programming language." > documents/python.txt
echo "Machine learning uses algorithms to learn from data." > documents/ml.txt
echo "The weather today is sunny." > documents/weather.txt

# Add to system
uv run python cli.py add-directory documents

# Query - system will filter out irrelevant "weather" document
uv run python cli.py query "Tell me about Python" --diagnostics
```

### Example 3: Web Search Fallback

```bash
# Query about something not in your documents
# System will detect low relevance and use web search
uv run python cli.py query "What is quantum entanglement?" --diagnostics
```

## Advanced Features

### Custom Relevance Grader

You can modify the relevance grading logic in `src/corrective_rag_system.py`:

```python
def grade_document_relevance(self, document: Document, question: str) -> Tuple[bool, str]:
    # Custom grading logic here
    pass
```

### Disable Web Search

If you want to use only local documents:

```python
rag = CorrectiveRAGSystem(use_web_search=False)
```

### Adjust Retrieval Count

```python
# Retrieve more documents for better coverage
result = rag.query("question", k=10)
```

## Troubleshooting

1. **No OpenAI API Key**: Set the `OPENAI_API_KEY` environment variable
2. **Web Search Issues**: DuckDuckGo search is rate-limited; reduce query frequency
3. **Low Relevance Scores**: Adjust `relevance_threshold` or improve document quality
4. **No documents found**: Make sure your documents are in supported formats (.txt)
5. **Vector store issues**: Try resetting with `uv run python cli.py reset`

## Performance Tips

1. **Optimize Chunk Size**: Smaller chunks (500-1000) work better for specific queries
2. **Adjust k Parameter**: More retrieved documents = better coverage but slower
3. **Tune Relevance Threshold**: Lower threshold = faster, higher = more accurate
4. **Use Better Embeddings**: `text-embedding-3-large` provides better semantic understanding

## Comparison: Traditional RAG vs Corrective RAG

| Feature | Traditional RAG | Corrective RAG |
|---------|----------------|----------------|
| Retrieval | ✅ Yes | ✅ Yes |
| Relevance Check | ❌ No | ✅ Yes |
| Filters Irrelevant Docs | ❌ No | ✅ Yes |
| Web Search Fallback | ❌ No | ✅ Yes |
| Diagnostics | ❌ Limited | ✅ Detailed |
| Self-Correction | ❌ No | ✅ Yes |

## Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements.

## License

This project is open source and available under the MIT License.

## References

- [LangChain Documentation](https://python.langchain.com/)
- [Corrective RAG Paper](https://arxiv.org/abs/2401.15884)
- [ChromaDB Documentation](https://docs.trychroma.com/)
- [OpenAI API Documentation](https://platform.openai.com/docs)

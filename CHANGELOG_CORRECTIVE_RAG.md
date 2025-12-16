# Changelog - Corrective RAG Implementation

## Version 2.0.0 - Corrective RAG Update

### 🎯 Major Changes

Converted the traditional RAG system into a **Corrective RAG (CRAG)** system with self-correction capabilities.

### ✨ New Features

#### 1. Relevance Grading System
- **LLM-based document grading**: Evaluates each retrieved document for relevance
- **Binary scoring**: Yes/No relevance decision for each document
- **Configurable threshold**: Adjust when to trigger web search fallback

#### 2. Self-Correction Mechanism
- **Automatic filtering**: Removes irrelevant documents before answer generation
- **Adaptive context**: Uses only relevant information for better accuracy
- **Quality assurance**: Reduces hallucination from irrelevant context

#### 3. Web Search Fallback
- **DuckDuckGo integration**: Searches web when local documents are insufficient
- **Automatic trigger**: Activates when relevance ratio falls below threshold
- **Configurable**: Can be enabled/disabled based on use case

#### 4. Comprehensive Diagnostics
- **Query-level insights**: See exactly how the system processes each query
- **Grading results**: View which documents were relevant/irrelevant
- **Web search tracking**: Know when and why web search was used
- **Performance metrics**: Relevance ratios and document counts

### 📁 New Files

```
src/
├── corrective_rag_system.py    # Core CRAG implementation (NEW)
└── rag_system.py               # Original RAG (kept for reference)

examples/
└── demo_corrective_rag.py      # Comprehensive demo script (NEW)

CORRECTIVE_RAG.md               # Technical documentation (NEW)
QUICKSTART.md                   # Quick start guide (NEW)
CHANGELOG_CORRECTIVE_RAG.md     # This file (NEW)
```

### 🔄 Modified Files

#### `src/api.py`
- Updated to use `CorrectiveRAGSystem`
- Added diagnostic support to API endpoints
- Enhanced status endpoint with CRAG-specific info
- Updated query endpoint to return diagnostics

**Breaking Changes:**
- Response model now includes optional `diagnostics` field
- Status response includes new fields: `system_type`, `relevance_threshold`, `web_search_enabled`

#### `src/cli.py`
- Migrated to `CorrectiveRAGSystem`
- Added `--diagnostics` flag to query command
- Enhanced status display with CRAG settings
- Improved interactive mode with real-time diagnostics
- Better visualization of grading results

#### `pyproject.toml`
- Version bumped to `0.2.0`
- Added `duckduckgo-search>=7.1.2` dependency
- Added `python-dotenv>=1.0.0` dependency
- Updated project description

#### `README.md`
- Complete rewrite focusing on Corrective RAG
- Added CRAG explanation and diagrams
- Enhanced usage examples with diagnostics
- Added comparison table (Traditional vs Corrective RAG)
- Detailed configuration guide
- Performance tips and troubleshooting

### 🎨 API Changes

#### New Request Parameters

**Query Request:**
```json
{
  "question": "string",
  "k": 4,
  "return_diagnostics": false  // NEW
}
```

**Query Response:**
```json
{
  "answer": "string",
  "sources": ["string"],
  "diagnostics": {              // NEW (optional)
    "total_retrieved": 4,
    "relevant_count": 2,
    "irrelevant_count": 2,
    "relevance_ratio": 0.5,
    "used_web_search": true,
    "web_search_results": "...",
    "grading_results": [...]
  }
}
```

### 🛠️ Configuration Options

New `CorrectiveRAGSystem` parameters:

```python
CorrectiveRAGSystem(
    openai_api_key="...",
    embedding_model="text-embedding-3-large",
    llm_model="gpt-3.5-turbo",
    chunk_size=1000,
    chunk_overlap=200,
    persist_directory="./chroma_db",
    relevance_threshold=0.6,     # NEW - default 0.6
    use_web_search=True          # NEW - default True
)
```

### 📊 Diagnostic Information

When `return_diagnostics=True`, you get:

| Field | Description |
|-------|-------------|
| `total_retrieved` | Total documents from vector store |
| `relevant_count` | Documents marked as relevant |
| `irrelevant_count` | Documents marked as irrelevant |
| `relevance_ratio` | Percentage of relevant documents |
| `used_web_search` | Whether web search was triggered |
| `web_search_results` | Web search content (if used) |
| `grading_results` | Individual grading for each doc |

### 🎯 CLI Enhancements

#### New Flags

```bash
# Query with diagnostics
cli.py query "question" --diagnostics

# Status shows CRAG configuration
cli.py status
# Output includes:
# - System Type: Corrective RAG
# - Relevance Threshold: 0.6
# - Web Search Enabled: True
```

#### Enhanced Output

- Color-coded relevance indicators (✓ = relevant, ✗ = irrelevant)
- Detailed diagnostic tables
- Web search usage notifications
- Grading results visualization

### 🔍 Technical Implementation

#### Relevance Grading Prompt

```
You are a grader assessing relevance of a retrieved document 
to a user question.

If the document contains keyword(s) or semantic meaning related 
to the question, grade it as relevant.

Give a binary score 'yes' or 'no' as JSON.
```

#### Decision Flow

```python
if relevant_docs:
    context.extend(relevant_docs)

if relevance_ratio < threshold and use_web_search:
    web_results = web_search(question)
    context.append(web_results)

answer = generate(question, context)
```

### 📈 Performance Impact

#### Latency
- **Traditional RAG**: ~1-2 seconds
- **Corrective RAG**: ~2-4 seconds (additional grading calls)
- **With Web Search**: +1-2 seconds when triggered

#### Cost
- **Traditional RAG**: Embeddings + 1 LLM call
- **Corrective RAG**: Embeddings + (k+1) LLM calls + optional web search
- **Example**: k=4 → 5 total LLM calls (4 grading + 1 generation)

#### Accuracy
- ✅ Improved answer quality (filters irrelevant info)
- ✅ Reduced hallucination
- ✅ Better handling of edge cases
- ✅ Fallback for missing information

### 🔄 Migration Guide

#### From v1.0.0 (Traditional RAG) to v2.0.0 (Corrective RAG)

**Python API:**
```python
# Old
from src.rag_system import RAGSystem
rag = RAGSystem()
rag.setup_qa_chain()
result = rag.query(question)

# New
from src.corrective_rag_system import CorrectiveRAGSystem
rag = CorrectiveRAGSystem(
    relevance_threshold=0.6,
    use_web_search=True
)
result = rag.query(question, return_diagnostics=True)
# No need for setup_qa_chain()
```

**CLI:**
```bash
# Old
python cli.py query "question"

# New (compatible, but enhanced)
python cli.py query "question"
python cli.py query "question" --diagnostics  # NEW
```

**API:**
```bash
# Old
curl -X POST "http://localhost:8000/query" \
  -d '{"question": "..."}'

# New (compatible, but enhanced)
curl -X POST "http://localhost:8000/query" \
  -d '{"question": "...", "return_diagnostics": true}'
```

### 🐛 Bug Fixes

- Fixed vectorstore persistence handling
- Improved error handling in web search
- Better JSON parsing for grading responses

### 📚 Documentation

#### New Documentation Files
- `CORRECTIVE_RAG.md` - Technical deep dive
- `QUICKSTART.md` - Quick start guide
- `examples/demo_corrective_rag.py` - Comprehensive demos

#### Updated Documentation
- `README.md` - Complete rewrite for CRAG
- Inline code comments improved

### 🔮 Future Improvements

Potential enhancements for future versions:

1. **Graded Relevance**: Use 0-1 scores instead of binary
2. **Query Rewriting**: Automatic query refinement
3. **Multi-hop Reasoning**: Follow-up queries
4. **Custom Search**: Specialized search engines
5. **Caching**: Cache grading results
6. **Async Processing**: Parallel document grading
7. **Metrics Dashboard**: Real-time performance monitoring

### 🙏 Credits

Based on:
- **Corrective RAG Paper**: https://arxiv.org/abs/2401.15884
- **LangChain Framework**: https://python.langchain.com/
- **ChromaDB**: https://docs.trychroma.com/

### 📝 Notes

- Original `RAGSystem` class kept in `src/rag_system.py` for reference
- All existing vector stores are compatible
- No data migration needed
- Backwards compatible API (new fields are optional)

---

## How to Use This Version

```bash
# Install new dependencies
uv sync

# Quick start
uv run python cli.py add-directory examples/sample_documents
uv run python cli.py query "What is Python?" --diagnostics

# Run demo
uv run python examples/demo_corrective_rag.py

# Start API server
uv run python main.py
```

For more information, see:
- [README.md](README.md) - Full documentation
- [CORRECTIVE_RAG.md](CORRECTIVE_RAG.md) - Technical details
- [QUICKSTART.md](QUICKSTART.md) - Quick start guide


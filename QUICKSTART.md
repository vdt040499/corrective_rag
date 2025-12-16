# Quick Start Guide - Corrective RAG

## Cài đặt nhanh (Vietnamese)

### 1. Cài đặt dependencies

```bash
# Cài đặt các package cần thiết
uv sync
```

### 2. Cấu hình API Key

```bash
# Tạo file .env
cp .env.example .env

# Chỉnh sửa .env và thêm OpenAI API key
# OPENAI_API_KEY=sk-...
```

### 3. Thêm tài liệu

```bash
# Thêm tài liệu mẫu
uv run python cli.py add-directory examples/sample_documents

# Kiểm tra trạng thái
uv run python cli.py status
```

### 4. Sử dụng

```bash
# Truy vấn cơ bản
uv run python cli.py query "Python là gì?"

# Truy vấn với chẩn đoán (xem quá trình tự sửa lỗi)
uv run python cli.py query "Python là gì?" --diagnostics

# Chế độ tương tác
uv run python cli.py interactive
```

## Quick Setup (English)

### 1. Install Dependencies

```bash
# Install required packages
uv sync
```

### 2. Configure API Key

```bash
# Create .env file
cp .env.example .env

# Edit .env and add your OpenAI API key
# OPENAI_API_KEY=sk-...
```

### 3. Add Documents

```bash
# Add sample documents
uv run python cli.py add-directory examples/sample_documents

# Check status
uv run python cli.py status
```

### 4. Start Using

```bash
# Basic query
uv run python cli.py query "What is Python?"

# Query with diagnostics (see self-correction in action)
uv run python cli.py query "What is Python?" --diagnostics

# Interactive mode
uv run python cli.py interactive
```

## What Makes This Different?

### Traditional RAG
```
Question → Retrieve Docs → Generate Answer
```
❌ Uses ALL retrieved documents (even irrelevant ones)
❌ No quality check
❌ No fallback if documents don't help

### Corrective RAG (This System)
```
Question → Retrieve Docs → Grade Relevance → Filter Bad Docs → Generate Answer
                                ↓
                        Not enough good docs?
                                ↓
                          Search the Web
```
✅ Evaluates each document's relevance
✅ Filters out irrelevant information
✅ Searches web if local docs aren't good enough
✅ Shows you exactly what it's doing (diagnostics)

## Example with Diagnostics

```bash
uv run python cli.py query "What is machine learning?" --diagnostics
```

You'll see:
- How many documents were retrieved
- Which ones were relevant vs irrelevant
- Whether web search was used
- The final answer with sources

## API Server

```bash
# Start server
uv run python main.py

# Open in browser
http://localhost:8000/docs
```

Test with curl:
```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is Python?",
    "return_diagnostics": true
  }'
```

## Demo Script

```bash
# Run the comprehensive demo
uv run python examples/demo_corrective_rag.py
```

## Customization

### Adjust Relevance Threshold

```python
from src.corrective_rag_system import CorrectiveRAGSystem

# Strict (uses web search more often)
rag = CorrectiveRAGSystem(relevance_threshold=0.9)

# Balanced (default)
rag = CorrectiveRAGSystem(relevance_threshold=0.6)

# Lenient (prefers local docs)
rag = CorrectiveRAGSystem(relevance_threshold=0.3)
```

### Disable Web Search

```python
# Local documents only
rag = CorrectiveRAGSystem(use_web_search=False)
```

## Common Commands

```bash
# View status
uv run python cli.py status

# Add your own documents
uv run python cli.py add-directory /path/to/your/documents

# Search without LLM
uv run python cli.py search "your search term"

# Analyze how documents are chunked
uv run python cli.py analyze-chunks path/to/file.txt

# Reset everything
uv run python cli.py reset
```

## Troubleshooting

**No API Key?**
```bash
export OPENAI_API_KEY='your-key-here'  # Linux/Mac
set OPENAI_API_KEY=your-key-here       # Windows CMD
$env:OPENAI_API_KEY='your-key-here'    # Windows PowerShell
```

**No Documents?**
```bash
uv run python cli.py add-directory examples/sample_documents
```

**Web Search Not Working?**
- DuckDuckGo search can be rate-limited
- Reduce query frequency
- Or disable with `use_web_search=False`

## Learn More

- **Full Documentation**: See [README.md](README.md)
- **Technical Details**: See [CORRECTIVE_RAG.md](CORRECTIVE_RAG.md)
- **Examples**: See `examples/demo_corrective_rag.py`

## Next Steps

1. ✅ Add your own documents
2. ✅ Try queries with `--diagnostics` flag
3. ✅ Experiment with different thresholds
4. ✅ Read [CORRECTIVE_RAG.md](CORRECTIVE_RAG.md) for technical details
5. ✅ Build your own application using the Python API

Enjoy your self-correcting RAG system! 🚀


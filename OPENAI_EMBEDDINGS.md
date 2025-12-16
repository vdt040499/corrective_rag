# OpenAI Embeddings Migration Guide

## Overview

The RAG project has been successfully migrated from HuggingFace embeddings to OpenAI embeddings for improved performance and quality.

## Changes Made

### 1. Dependencies
- **Removed**: `sentence-transformers` dependency
- **Updated**: Using `langchain-openai` for both embeddings and LLM

### 2. Embedding Model
- **Before**: `sentence-transformers/all-MiniLM-L6-v2` (HuggingFace)
- **After**: `text-embedding-3-small` (OpenAI)

### 3. Configuration
- **API Key Required**: OpenAI API key is now required for both embeddings and Q&A
- **Environment Variable**: Set `OPENAI_API_KEY` in your environment or `.env` file

## Benefits of OpenAI Embeddings

### Quality Improvements
- **Higher Semantic Understanding**: Better comprehension of context and meaning
- **Multilingual Support**: Improved performance across different languages
- **Domain Consistency**: More consistent results across various domains
- **Latest Technology**: Access to OpenAI's state-of-the-art embedding models

### Operational Benefits
- **No Local Downloads**: No need to download large model files
- **Consistent Performance**: Same performance across different machines
- **Regular Updates**: Automatic access to model improvements
- **Scalability**: No local compute requirements for embeddings

## Setup Instructions

### 1. Get OpenAI API Key
1. Visit [OpenAI Platform](https://platform.openai.com/)
2. Create an account or sign in
3. Navigate to API Keys section
4. Create a new API key
5. Copy the key (starts with `sk-`)

### 2. Configure Environment
```bash
# Option 1: Environment variable
export OPENAI_API_KEY="sk-your-api-key-here"

# Option 2: .env file
echo "OPENAI_API_KEY=sk-your-api-key-here" > .env
```

### 3. Reset Vector Store
Since embeddings are incompatible between models, reset your vector store:
```bash
# Remove existing vector store
rm -rf chroma_db/

# Or use the CLI
uv run python cli.py reset
```

## Usage Examples

### Basic Usage
```python
from src.rag_system import RAGSystem

# Initialize with OpenAI embeddings
rag = RAGSystem(
    openai_api_key="sk-your-api-key-here",
    embedding_model="text-embedding-3-small"
)

# Load and process documents
documents = rag.load_documents_from_directory("./documents")
rag.add_documents(documents)

# Search with OpenAI embeddings
results = rag.similarity_search("your query", k=5)
```

### CLI Usage
```bash
# Check status
uv run python cli.py status

# Add documents (requires API key)
uv run python cli.py add-directory ./documents

# Search documents
uv run python cli.py search "your query"

# Ask questions
uv run python cli.py query "What is the main topic?"
```

### API Usage
```bash
# Start the API server
uv run python main.py

# Test with curl
curl -X POST "http://localhost:8000/search" \
  -H "Content-Type: application/json" \
  -d '{"query": "your search query", "k": 3}'
```

## Available Embedding Models

OpenAI offers several embedding models:

- **text-embedding-3-small**: Best balance of performance and cost (default)
- **text-embedding-3-large**: Highest performance, higher cost
- **text-embedding-ada-002**: Previous generation, still supported

### Changing Embedding Model
```python
# Use the large model for better performance
rag = RAGSystem(
    openai_api_key="your-key",
    embedding_model="text-embedding-3-large"
)
```

## Cost Considerations

### Pricing (as of 2024)
- **text-embedding-3-small**: $0.00002 per 1K tokens
- **text-embedding-3-large**: $0.00013 per 1K tokens

### Cost Estimation
For typical documents:
- 1,000 words ≈ 750 tokens
- Processing 100 documents (100K words) ≈ 75K tokens
- Cost with small model: ~$1.50
- Cost with large model: ~$9.75

### Cost Optimization Tips
1. **Chunk Size**: Optimize chunk size to reduce redundancy
2. **Batch Processing**: Process documents in batches
3. **Caching**: Vector store persists embeddings (no re-processing)
4. **Model Selection**: Use small model unless you need maximum performance

## Troubleshooting

### Common Issues

#### 1. API Key Not Found
```
Error: No OpenAI API key provided
```
**Solution**: Set the `OPENAI_API_KEY` environment variable

#### 2. API Key Invalid
```
Error: Incorrect API key provided
```
**Solution**: Verify your API key is correct and active

#### 3. Rate Limits
```
Error: Rate limit exceeded
```
**Solution**: Implement retry logic or reduce request frequency

#### 4. Incompatible Vector Store
```
Error: Vector store dimension mismatch
```
**Solution**: Reset the vector store (`rm -rf chroma_db/`)

### Debug Mode
```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Test embeddings
rag = RAGSystem(openai_api_key="your-key")
print(f"Embeddings initialized: {rag.embeddings is not None}")
```

## Migration Checklist

- [ ] Obtain OpenAI API key
- [ ] Set `OPENAI_API_KEY` environment variable
- [ ] Reset existing vector store
- [ ] Test with sample documents
- [ ] Update any custom code using embeddings
- [ ] Monitor API usage and costs
- [ ] Update documentation for your team

## Performance Comparison

| Aspect | HuggingFace | OpenAI |
|--------|-------------|---------|
| Setup | Download models | API key only |
| Quality | Good | Excellent |
| Speed | Fast (local) | Fast (API) |
| Cost | Free | Pay per use |
| Maintenance | Model updates | Automatic |
| Offline | Yes | No |

## Next Steps

1. **Test the System**: Use the test script to verify everything works
2. **Process Your Documents**: Add your actual documents to the system
3. **Monitor Usage**: Keep track of API usage and costs
4. **Optimize**: Adjust chunk sizes and models based on your needs
5. **Scale**: Consider batch processing for large document sets

For questions or issues, refer to the main README.md or create an issue in the project repository.

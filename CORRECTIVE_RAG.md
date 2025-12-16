# Corrective RAG (CRAG) - Technical Documentation

## Overview

Corrective RAG (CRAG) is an advanced Retrieval-Augmented Generation technique that improves upon traditional RAG by introducing self-correction mechanisms. This document explains the technical implementation and benefits of our CRAG system.

## Architecture

### Traditional RAG Flow
```
Query → Retrieve Documents → Generate Answer
```

### Corrective RAG Flow
```
Query → Retrieve Documents → Grade Relevance → Filter/Correct → Generate Answer
                                    ↓
                            Low Relevance?
                                    ↓
                            Web Search Fallback
```

## Key Components

### 1. Document Retrieval
- Uses ChromaDB vector store with OpenAI embeddings
- Semantic similarity search
- Configurable number of documents (k parameter)

```python
retrieved_docs = self.vectorstore.similarity_search(question, k=4)
```

### 2. Relevance Grading

The system uses an LLM-based grader to evaluate each retrieved document:

```python
def grade_document_relevance(self, document: Document, question: str) -> Tuple[bool, str]:
    """
    Evaluates if a document is relevant to the question
    Returns: (is_relevant: bool, raw_response: str)
    """
```

**Grading Prompt:**
```
You are a grader assessing relevance of a retrieved document to a user question.

If the document contains keyword(s) or semantic meaning related to the question,
grade it as relevant.

Give a binary score 'yes' or 'no'.
```

### 3. Self-Correction Logic

The system makes decisions based on relevance ratio:

```python
relevance_ratio = len(relevant_docs) / len(retrieved_docs)

if relevance_ratio < self.relevance_threshold:
    # Trigger web search fallback
    web_results = self.web_search_fallback(question)
    context_parts.append(web_results)
```

### 4. Web Search Fallback

When local documents are insufficient:

```python
# Uses DuckDuckGo search
self.web_search = DuckDuckGoSearchResults(num_results=3)
results = self.web_search.run(question)
```

### 5. Answer Generation

Combines relevant documents and web results:

```python
context = "\n\n".join([
    *[doc.page_content for doc in relevant_docs],
    web_search_results  # if relevance is low
])

answer = self.answer_generator.run(
    question=question,
    context=context
)
```

## Configuration Parameters

### Relevance Threshold

Controls when to trigger web search:

| Threshold | Behavior | Use Case |
|-----------|----------|----------|
| 0.8-1.0 | Strict | High accuracy required, willing to use web search |
| 0.5-0.7 | Balanced | General use, balanced approach |
| 0.0-0.4 | Lenient | Prefer local docs, minimal web search |

```python
rag = CorrectiveRAGSystem(relevance_threshold=0.6)
```

### Web Search Toggle

```python
# Enable web search (default)
rag = CorrectiveRAGSystem(use_web_search=True)

# Disable web search (local only)
rag = CorrectiveRAGSystem(use_web_search=False)
```

### Retrieval Count (k)

Number of documents to retrieve:

```python
# More documents = better coverage, slower
result = rag.query(question, k=10)

# Fewer documents = faster, might miss context
result = rag.query(question, k=2)
```

## Diagnostic Information

Enable diagnostics to understand the correction process:

```python
result = rag.query(question, return_diagnostics=True)

diagnostics = result["diagnostics"]
```

### Diagnostic Fields

```python
{
    "total_retrieved": 4,           # Total docs retrieved from vector store
    "relevant_count": 2,             # Docs marked as relevant
    "irrelevant_count": 2,           # Docs marked as irrelevant
    "relevance_ratio": 0.5,          # Percentage of relevant docs
    "used_web_search": True,         # Whether web search was triggered
    "web_search_results": "...",     # Web search content (if used)
    "grading_results": [             # Individual document grades
        {
            "content_preview": "...",
            "is_relevant": True,
            "grade_response": '{"score": "yes"}'
        }
    ]
}
```

## Implementation Details

### Relevance Grader Chain

```python
def _setup_relevance_grader(self):
    relevance_prompt = PromptTemplate(
        template="""You are a grader assessing relevance...
        
        Document: {document}
        Question: {question}
        
        Score as JSON: {{"score": "yes"}} or {{"score": "no"}}
        """,
        input_variables=["document", "question"]
    )
    
    self.relevance_grader = LLMChain(
        llm=self.llm,
        prompt=relevance_prompt
    )
```

### Answer Generator Chain

```python
def _setup_answer_generator(self):
    answer_prompt = PromptTemplate(
        template="""Use the following context to answer the question.
        
        Question: {question}
        Context: {context}
        
        Answer:""",
        input_variables=["question", "context"]
    )
    
    self.answer_generator = LLMChain(
        llm=self.llm,
        prompt=answer_prompt
    )
```

## Performance Considerations

### Latency

Corrective RAG adds overhead:

1. **Relevance Grading**: LLM call for each retrieved document
2. **Web Search**: Network request if triggered

**Optimization strategies:**
- Reduce `k` to retrieve fewer documents
- Use faster LLM models for grading
- Cache grading results for similar queries
- Adjust threshold to reduce web search frequency

### Cost

OpenAI API costs:
- Embeddings: Per document chunk
- Relevance grading: Per retrieved document
- Answer generation: Per query
- Total cost ≈ Traditional RAG + (k × grading_cost)

### Accuracy

Improvements over traditional RAG:
- ✅ Filters irrelevant documents
- ✅ Reduces hallucination from irrelevant context
- ✅ Provides fallback for missing information
- ✅ Transparent decision-making via diagnostics

## Use Cases

### 1. Domain-Specific QA with Web Fallback

```python
# Local technical documentation + web for latest updates
rag = CorrectiveRAGSystem(
    relevance_threshold=0.7,
    use_web_search=True
)
```

### 2. High-Precision Applications

```python
# Medical/Legal: Only use highly relevant docs
rag = CorrectiveRAGSystem(
    relevance_threshold=0.9,
    use_web_search=False  # Don't use unverified web sources
)
```

### 3. General Knowledge Assistant

```python
# Balance between local and web
rag = CorrectiveRAGSystem(
    relevance_threshold=0.6,
    use_web_search=True
)
```

## Limitations

1. **Additional Latency**: Grading adds LLM calls
2. **Cost**: More API calls than traditional RAG
3. **Web Search Quality**: DuckDuckGo results may vary
4. **Binary Grading**: Current implementation uses yes/no (could use scores)
5. **Rate Limits**: Web search may be rate-limited

## Future Enhancements

Potential improvements:

1. **Graded Relevance Scores**: Use 0-1 scores instead of binary
2. **Query Rewriting**: Rephrase queries for better retrieval
3. **Multi-hop Reasoning**: Follow-up queries based on initial results
4. **Custom Web Search**: Use specialized search engines
5. **Caching**: Cache grading results and web searches
6. **Async Processing**: Parallel grading for faster processing

## Example Workflows

### Workflow 1: All Documents Relevant

```
Query: "What is Python?"
↓
Retrieve: 4 docs about Python
↓
Grade: 4/4 relevant (ratio = 1.0)
↓
Decision: Use all docs, no web search
↓
Generate: Answer from local docs
```

### Workflow 2: Mixed Relevance

```
Query: "Explain machine learning"
↓
Retrieve: 4 docs (2 ML, 2 unrelated)
↓
Grade: 2/4 relevant (ratio = 0.5)
↓
Decision: Filter + web search (ratio < 0.6)
↓
Generate: Answer from 2 relevant docs + web results
```

### Workflow 3: No Relevant Documents

```
Query: "Latest quantum computing news"
↓
Retrieve: 4 docs (none relevant)
↓
Grade: 0/4 relevant (ratio = 0.0)
↓
Decision: Web search only
↓
Generate: Answer from web results
```

## Comparison Table

| Feature | Traditional RAG | Corrective RAG |
|---------|----------------|----------------|
| Retrieval | Vector search | Vector search |
| Relevance Check | ❌ None | ✅ LLM-based grading |
| Document Filtering | ❌ No | ✅ Yes |
| Web Fallback | ❌ No | ✅ Configurable |
| Diagnostics | ❌ Limited | ✅ Comprehensive |
| Latency | Low | Medium |
| Cost | Lower | Higher |
| Accuracy | Good | Better |
| Transparency | Low | High |

## References

- **Original CRAG Paper**: [Corrective Retrieval Augmented Generation](https://arxiv.org/abs/2401.15884)
- **LangChain**: https://python.langchain.com/
- **ChromaDB**: https://docs.trychroma.com/
- **OpenAI Embeddings**: https://platform.openai.com/docs/guides/embeddings

## Getting Started

See the main [README.md](README.md) for installation and usage instructions.

Try the demo:
```bash
uv run python examples/demo_corrective_rag.py
```

Or use the CLI with diagnostics:
```bash
uv run python cli.py query "Your question" --diagnostics
```


#!/usr/bin/env python3
"""
Demo script for RAG system with OpenAI embeddings
"""

import os
import sys
from pathlib import Path

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("Warning: python-dotenv not installed. Using system environment variables only.")

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
print(project_root)

from src.rag_system import RAGSystem


def main():
    """Run the OpenAI embeddings demo"""
    print("🚀 RAG System Demo with OpenAI Embeddings")
    print("=" * 60)
    
    # Check for OpenAI API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OpenAI API key not found!")
        print("Please set the OPENAI_API_KEY environment variable:")
        print("export OPENAI_API_KEY='your-api-key-here'")
        print("\nOr create a .env file with:")
        print("OPENAI_API_KEY=your-api-key-here")
        return
    
    print(f"✅ OpenAI API key found: {api_key[:8]}...")
    
    # Initialize RAG system with OpenAI embeddings
    print("\n1. Initializing RAG system with OpenAI embeddings...")
    embedding_model = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
    llm_model = os.getenv("LLM_MODEL", "gpt-3.5-turbo")

    rag = RAGSystem(
        openai_api_key=api_key,
        embedding_model=embedding_model,
        llm_model=llm_model
    )
    
    print(f"   Embedding model: {rag.embedding_model}")
    print(f"   LLM model: {rag.llm_model}")
    
    # Check if we have sample documents
    sample_docs_dir = Path(__file__).parent / "sample_documents"
    if not sample_docs_dir.exists():
        print("❌ Sample documents directory not found!")
        return
    
    # Load documents
    print("\n2. Loading sample documents...")
    documents = rag.load_documents_from_directory(str(sample_docs_dir))
    print(f"   Loaded {len(documents)} documents")
    
    # Add documents to vector store
    print("\n3. Creating embeddings and adding to vector store...")
    print("   (This may take a moment as we call OpenAI's embedding API)")
    try:
        rag.add_documents(documents)
        print("   ✅ Documents successfully embedded and stored!")
    except Exception as e:
        print(f"   ❌ Error creating embeddings: {e}")
        return
    
    # Get collection info
    info = rag.get_collection_info()
    print(f"   Status: {info['status']}")
    print(f"   Document count: {info['document_count']}")
    
    # Perform similarity search
    print("\n4. Testing similarity search with OpenAI embeddings...")
    search_queries = [
        "What is Python programming?",
        "machine learning algorithms and applications",
        "web development frameworks"
    ]
    
    for query in search_queries:
        print(f"\n   Query: '{query}'")
        try:
            results = rag.similarity_search(query, k=2)
            for i, doc in enumerate(results, 1):
                source = doc.metadata.get('source', 'Unknown')
                content_preview = doc.page_content[:150] + "..."
                print(f"   {i}. Source: {Path(source).name}")
                print(f"      Preview: {content_preview}")
        except Exception as e:
            print(f"   ❌ Search error: {e}")
    
    # Test QA functionality
    print("\n5. Testing Question Answering with OpenAI...")
    try:
        rag.setup_qa_chain()
        
        qa_questions = [
            "What are the main features of Python?",
            "What types of machine learning exist?",
            "Which web framework is recommended for large applications?"
        ]
        
        for question in qa_questions:
            print(f"\n   Question: {question}")
            try:
                result = rag.query(question)
                answer = result['answer']
                sources = len(result['source_documents'])
                print(f"   Answer: {answer[:200]}...")
                print(f"   Sources used: {sources} documents")
            except Exception as e:
                print(f"   ❌ QA error: {e}")
                
    except Exception as e:
        print(f"   ❌ QA setup failed: {e}")
    
    print("\n✅ OpenAI embeddings demo completed!")
    print("\nKey benefits of OpenAI embeddings:")
    print("- Higher quality semantic understanding")
    print("- Better multilingual support")
    print("- Consistent performance across domains")
    print("- No local model download required")
    print("\nNote: Using OpenAI embeddings requires API calls and may incur costs.")


if __name__ == "__main__":
    main()

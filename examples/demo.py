#!/usr/bin/env python3
"""
Demo script for RAG system
"""

import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.rag_system import RAGSystem


def main():
    """Run the demo"""
    print("🚀 RAG System Demo")
    print("=" * 50)
    
    # Initialize RAG system
    print("\n1. Initializing RAG system...")
    rag = RAGSystem()
    
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
    print("\n3. Adding documents to vector store...")
    rag.add_documents(documents)
    
    # Get collection info
    info = rag.get_collection_info()
    print(f"   Status: {info['status']}")
    print(f"   Document count: {info['document_count']}")
    
    # Perform similarity search
    print("\n4. Testing similarity search...")
    search_queries = [
        "What is Python?",
        "machine learning algorithms",
        "web frameworks"
    ]
    
    for query in search_queries:
        print(f"\n   Query: '{query}'")
        results = rag.similarity_search(query, k=2)
        for i, doc in enumerate(results, 1):
            source = doc.metadata.get('source', 'Unknown')
            content_preview = doc.page_content[:100] + "..."
            print(f"   {i}. Source: {Path(source).name}")
            print(f"      Preview: {content_preview}")
    
    # Test QA if OpenAI API key is available
    if os.getenv("OPENAI_API_KEY"):
        print("\n5. Testing Question Answering...")
        try:
            rag.setup_qa_chain()
            
            qa_questions = [
                "What are the key features of Python?",
                "What types of machine learning are there?",
                "Which Python web framework is best for large applications?"
            ]
            
            for question in qa_questions:
                print(f"\n   Question: {question}")
                result = rag.query(question)
                print(f"   Answer: {result['answer'][:200]}...")
                
        except Exception as e:
            print(f"   ❌ QA test failed: {e}")
    else:
        print("\n5. Skipping QA test (no OpenAI API key)")
        print("   Set OPENAI_API_KEY environment variable to test QA functionality")
    
    print("\n✅ Demo completed!")
    print("\nNext steps:")
    print("- Set OPENAI_API_KEY to test question answering")
    print("- Try the CLI: python cli.py --help")
    print("- Start the API: python main.py")
    print("- Add your own documents to test with real data")


if __name__ == "__main__":
    main()

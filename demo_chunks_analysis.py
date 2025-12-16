#!/usr/bin/env python3
"""
Demo script to show document chunking and embedding analysis
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

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.rag_system import RAGSystem


def main():
    """Demo document chunking and embedding analysis"""
    print("📄 Document Chunking & Embedding Analysis Demo")
    print("=" * 60)
    
    # Check for OpenAI API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OpenAI API key not found!")
        print("Please set the OPENAI_API_KEY environment variable")
        return
    
    print(f"✅ OpenAI API key found: {api_key[:8]}...")
    
    # Initialize RAG system
    embedding_model = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
    rag = RAGSystem(
        openai_api_key=api_key,
        embedding_model=embedding_model,
        chunk_size=500,  # Smaller chunks for demo
        chunk_overlap=50
    )
    
    print(f"📊 Configuration:")
    print(f"   Embedding model: {rag.embedding_model}")
    print(f"   Chunk size: {rag.chunk_size}")
    print(f"   Chunk overlap: {rag.chunk_overlap}")
    
    # Sample document path
    sample_doc = Path(__file__).parent / "examples" / "sample_documents" / "python_intro.txt"
    
    if not sample_doc.exists():
        print(f"❌ Sample document not found: {sample_doc}")
        return
    
    print(f"\n📖 Analyzing document: {sample_doc.name}")
    
    try:
        # Analyze the document
        print("🔄 Generating embeddings for each chunk...")
        analysis = rag.analyze_document_chunks(str(sample_doc))
        
        print(f"\n📈 Analysis Results:")
        print(f"   Original length: {analysis['original_length']:,} characters")
        print(f"   Original words: {analysis['original_word_count']:,} words")
        print(f"   Total chunks: {analysis['total_chunks']}")
        print(f"   Embedding dimension: {analysis['chunks'][0]['embedding_dimension']}")
        
        print(f"\n🧩 Chunk Details:")
        print("-" * 60)
        
        for chunk in analysis['chunks']:
            print(f"\nChunk {chunk['chunk_id']}:")
            print(f"  📏 Length: {chunk['content_length']} chars, {chunk['word_count']} words")
            print(f"  🔢 Embedding norm: {chunk['embedding_norm']:.4f}")
            
            # Show content preview
            content = chunk['content']
            preview = content[:100] + "..." if len(content) > 100 else content
            print(f"  📝 Content: {preview}")
            
            # Show embedding preview
            embedding_preview = chunk['embedding_vector'][:5]
            print(f"  🎯 Embedding (first 5): [{', '.join([f'{x:.3f}' for x in embedding_preview])}, ...]")
        
        # Show embedding statistics
        print(f"\n📊 Embedding Statistics:")
        norms = [chunk['embedding_norm'] for chunk in analysis['chunks']]
        print(f"   Min norm: {min(norms):.4f}")
        print(f"   Max norm: {max(norms):.4f}")
        print(f"   Avg norm: {sum(norms)/len(norms):.4f}")
        
        # Calculate similarity between chunks (if available)
        if len(analysis['chunks']) >= 2:
            chunk1_vec = analysis['chunks'][0]['embedding_vector']
            chunk2_vec = analysis['chunks'][1]['embedding_vector']
            
            # Cosine similarity
            dot_product = sum(a * b for a, b in zip(chunk1_vec, chunk2_vec))
            norm1 = analysis['chunks'][0]['embedding_norm']
            norm2 = analysis['chunks'][1]['embedding_norm']
            similarity = dot_product / (norm1 * norm2)
            
            print(f"\n🔗 Chunk Similarity:")
            print(f"   Cosine similarity between chunk 1 & 2: {similarity:.4f}")
            print(f"   (Higher values = more similar content)")
        
        print(f"\n✅ Analysis completed!")
        print(f"\n💡 Key Insights:")
        print(f"   • Each chunk gets converted to a {analysis['chunks'][0]['embedding_dimension']}-dimensional vector")
        print(f"   • OpenAI embeddings are normalized (norm ≈ 1.0)")
        print(f"   • Chunk overlap helps maintain context between segments")
        print(f"   • Similar content produces similar embedding vectors")
        
        print(f"\n🔧 CLI Commands:")
        print(f"   uv run python cli.py analyze-chunks {sample_doc}")
        print(f"   uv run python cli.py analyze-chunks {sample_doc} --show-vectors")
        
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

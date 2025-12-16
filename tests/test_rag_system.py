"""
Tests for RAG system
"""

import pytest
import tempfile
import os
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.rag_system import RAGSystem


@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing"""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


@pytest.fixture
def sample_documents(temp_dir):
    """Create sample documents for testing"""
    doc1_path = Path(temp_dir) / "doc1.txt"
    doc2_path = Path(temp_dir) / "doc2.txt"
    
    doc1_path.write_text("Python is a programming language used for web development and data science.")
    doc2_path.write_text("Machine learning is a subset of artificial intelligence that uses algorithms.")
    
    return [str(doc1_path), str(doc2_path)]


@pytest.fixture
def rag_system(temp_dir):
    """Create a RAG system instance for testing"""
    persist_dir = Path(temp_dir) / "test_chroma"
    return RAGSystem(
        openai_api_key="test-key",  # Mock key for testing
        persist_directory=str(persist_dir)
    )


def test_rag_system_initialization():
    """Test RAG system initialization"""
    rag = RAGSystem()
    assert rag.embedding_model == "text-embedding-3-small"
    assert rag.chunk_size == 1000
    assert rag.chunk_overlap == 200
    assert rag.vectorstore is None
    assert rag.embeddings is None  # No API key provided


def test_load_documents_from_files(rag_system, sample_documents):
    """Test loading documents from files"""
    documents = rag_system.load_documents_from_files(sample_documents)
    
    assert len(documents) == 2
    assert "Python is a programming language" in documents[0].page_content
    assert "Machine learning is a subset" in documents[1].page_content


def test_load_documents_from_directory(rag_system, temp_dir, sample_documents):
    """Test loading documents from directory"""
    documents = rag_system.load_documents_from_directory(temp_dir, "*.txt")
    
    assert len(documents) == 2


def test_add_documents(rag_system, sample_documents):
    """Test adding documents to vector store"""
    documents = rag_system.load_documents_from_files(sample_documents)
    rag_system.add_documents(documents)
    
    assert rag_system.vectorstore is not None
    
    # Test collection info
    info = rag_system.get_collection_info()
    assert info["status"] == "Vector store active"
    assert info["document_count"] > 0


def test_similarity_search(rag_system, sample_documents):
    """Test similarity search"""
    documents = rag_system.load_documents_from_files(sample_documents)
    rag_system.add_documents(documents)
    
    results = rag_system.similarity_search("programming language", k=1)
    
    assert len(results) == 1
    assert "Python" in results[0].page_content


def test_vectorstore_persistence(temp_dir, sample_documents):
    """Test vector store persistence"""
    persist_dir = Path(temp_dir) / "test_chroma"
    
    # Create first RAG system and add documents
    rag1 = RAGSystem(persist_directory=str(persist_dir))
    documents = rag1.load_documents_from_files(sample_documents)
    rag1.add_documents(documents)
    
    # Create second RAG system and load existing vector store
    rag2 = RAGSystem(persist_directory=str(persist_dir))
    loaded = rag2.load_vectorstore()
    
    assert loaded is True
    assert rag2.vectorstore is not None
    
    # Test that documents are still there
    results = rag2.similarity_search("programming", k=1)
    assert len(results) > 0


def test_get_collection_info_no_vectorstore(rag_system):
    """Test collection info when no vector store exists"""
    info = rag_system.get_collection_info()
    assert info["status"] == "No vector store initialized"


if __name__ == "__main__":
    pytest.main([__file__])

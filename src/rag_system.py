"""
RAG System Implementation using LangChain and ChromaDB
"""

import os
from typing import List, Optional
from pathlib import Path

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader, DirectoryLoader
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.chains import RetrievalQA
from langchain.schema import Document
from langchain.prompts import PromptTemplate


class RAGSystem:
    """
    A complete RAG (Retrieval-Augmented Generation) system
    """
    
    def __init__(
        self,
        openai_api_key: Optional[str] = None,
        embedding_model: str = "text-embedding-3-large",
        llm_model: str = "gpt-3.5-turbo",
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        persist_directory: str = "./chroma_db"
    ):
        """
        Initialize the RAG system

        Args:
            openai_api_key: OpenAI API key
            embedding_model: OpenAI embedding model name
            llm_model: OpenAI model name
            chunk_size: Size of text chunks
            chunk_overlap: Overlap between chunks
            persist_directory: Directory to persist ChromaDB
        """
        self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        self.embedding_model = embedding_model
        self.llm_model = llm_model
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.persist_directory = persist_directory
        
        # Initialize components
        if self.openai_api_key:
            self.embeddings = OpenAIEmbeddings(
                openai_api_key=self.openai_api_key,
                model=self.embedding_model
            )
        else:
            # Fallback to a simple embedding if no API key
            print("Warning: No OpenAI API key provided. Embedding functionality will be limited.")
            self.embeddings = None
        
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len,
        )
        
        self.vectorstore = None
        self.qa_chain = None
        
        # Initialize LLM if API key is provided
        if self.openai_api_key:
            self.llm = ChatOpenAI(
                openai_api_key=self.openai_api_key,
                model_name=self.llm_model,
                temperature=0
            )
        else:
            self.llm = None
            print("Warning: No OpenAI API key provided. QA functionality will be limited.")
    
    def load_documents_from_directory(self, directory_path: str, glob_pattern: str = "**/*.txt") -> List[Document]:
        """
        Load documents from a directory
        
        Args:
            directory_path: Path to the directory containing documents
            glob_pattern: Pattern to match files
            
        Returns:
            List of loaded documents
        """
        loader = DirectoryLoader(
            directory_path,
            glob=glob_pattern,
            loader_cls=TextLoader
        )
        documents = loader.load()
        return documents
    
    def load_documents_from_files(self, file_paths: List[str]) -> List[Document]:
        """
        Load documents from specific files
        
        Args:
            file_paths: List of file paths
            
        Returns:
            List of loaded documents
        """
        documents = []
        for file_path in file_paths:
            loader = TextLoader(file_path)
            docs = loader.load()
            documents.extend(docs)
        return documents
    
    def add_documents(self, documents: List[Document]) -> None:
        """
        Add documents to the vector store

        Args:
            documents: List of documents to add
        """
        if self.embeddings is None:
            raise ValueError("Embeddings not initialized. Please provide OpenAI API key.")

        # Split documents into chunks
        texts = self.text_splitter.split_documents(documents)

        if self.vectorstore is None:
            # Create new vector store
            self.vectorstore = Chroma.from_documents(
                documents=texts,
                embedding=self.embeddings,
                persist_directory=self.persist_directory
            )
        else:
            # Add to existing vector store
            self.vectorstore.add_documents(texts)

        # Persist the vector store
        self.vectorstore.persist()

        print(f"Added {len(texts)} text chunks to the vector store.")
    
    def load_vectorstore(self) -> bool:
        """
        Load existing vector store from disk

        Returns:
            True if loaded successfully, False otherwise
        """
        if self.embeddings is None:
            print("Warning: Cannot load vector store without embeddings. Please provide OpenAI API key.")
            return False

        try:
            if Path(self.persist_directory).exists():
                self.vectorstore = Chroma(
                    persist_directory=self.persist_directory,
                    embedding_function=self.embeddings
                )
                print("Vector store loaded successfully.")
                return True
            else:
                print("No existing vector store found.")
                return False
        except Exception as e:
            print(f"Error loading vector store: {e}")
            return False
    
    def setup_qa_chain(self, retriever_k: int = 4, use_strict_context: bool = False) -> None:
        """
        Setup the QA chain
        
        Args:
            retriever_k: Number of documents to retrieve
            use_strict_context: If True, force LLM to only use provided context (ignore its own knowledge)
        """
        if self.vectorstore is None:
            raise ValueError("Vector store not initialized. Please add documents first.")
        
        if self.llm is None:
            raise ValueError("LLM not initialized. Please provide OpenAI API key.")
        
        retriever = self.vectorstore.as_retriever(
            search_kwargs={"k": retriever_k}
        )
        
        # Use strict prompt that forces LLM to only rely on context
        if use_strict_context:
            prompt_template = """Bạn là một trợ lý. Trả lời câu hỏi dựa HOÀN TOÀN vào tài liệu được cung cấp. KHÔNG dùng bất kỳ kiến thức nào khác.

QUY TẮC BẮT BUỘC:
1. CHỈ dùng thông tin từ tài liệu bên dưới
2. PHẢI trả lời, KHÔNG được nói "tài liệu không có", "không đủ thông tin"
3. Bắt đầu trả lời ngay, đi thẳng vào đáp án
4. QUAN TRỌNG: Nếu câu hỏi hỏi về phiên bản mới (ví dụ: iPhone 15) mà tài liệu CHỈ có về phiên bản cũ (ví dụ: iPhone 14), hãy GIẢ ĐỊNH phiên bản mới GIỐNG HỆT phiên bản cũ (vì tài liệu không nói gì về sự thay đổi)
5. Ví dụ: Nếu tài liệu nói "iPhone 14 dùng Lightning" và câu hỏi hỏi "iPhone 15 dùng gì?", trả lời "iPhone 15 cũng dùng Lightning" (vì tài liệu không đề cập sự thay đổi)
6. Trả lời bằng tiếng Việt

Tài liệu:
{context}

Câu hỏi: {question}

ĐÁP ÁN:"""
            
            QA_PROMPT = PromptTemplate(
                template=prompt_template,
                input_variables=["context", "question"]
            )
            
            self.qa_chain = RetrievalQA.from_chain_type(
                llm=self.llm,
                chain_type="stuff",
                retriever=retriever,
                return_source_documents=True,
                chain_type_kwargs={"prompt": QA_PROMPT}
            )
        else:
            self.qa_chain = RetrievalQA.from_chain_type(
                llm=self.llm,
                chain_type="stuff",
                retriever=retriever,
                return_source_documents=True
            )
        
        print("QA chain setup completed.")
    
    def query(self, question: str) -> dict:
        """
        Query the RAG system

        Args:
            question: Question to ask

        Returns:
            Dictionary containing answer and source documents
        """
        if self.qa_chain is None:
            raise ValueError("QA chain not setup. Please call setup_qa_chain() first.")

        result = self.qa_chain.invoke({"query": question})

        return {
            "answer": result["result"],
            "source_documents": result["source_documents"]
        }
    
    def similarity_search(self, query: str, k: int = 4) -> List[Document]:
        """
        Perform similarity search without LLM
        
        Args:
            query: Search query
            k: Number of documents to return
            
        Returns:
            List of similar documents
        """
        if self.vectorstore is None:
            raise ValueError("Vector store not initialized. Please add documents first.")
        
        return self.vectorstore.similarity_search(query, k=k)
    
    def analyze_document_chunks(self, file_path: str) -> dict:
        """
        Analyze how a document is split into chunks and show embeddings

        Args:
            file_path: Path to the document file

        Returns:
            Dictionary with chunk analysis information
        """
        if self.embeddings is None:
            raise ValueError("Embeddings not initialized. Please provide OpenAI API key.")

        # Load the document
        from langchain_community.document_loaders import TextLoader
        loader = TextLoader(file_path)
        documents = loader.load()

        if not documents:
            return {"error": "No documents found"}

        document = documents[0]

        # Split into chunks
        chunks = self.text_splitter.split_documents([document])

        # Get embeddings for each chunk
        chunk_analysis = []
        for i, chunk in enumerate(chunks):
            # Get embedding vector
            embedding_vector = self.embeddings.embed_query(chunk.page_content)

            chunk_info = {
                "chunk_id": i + 1,
                "content": chunk.page_content,
                "content_length": len(chunk.page_content),
                "word_count": len(chunk.page_content.split()),
                "embedding_dimension": len(embedding_vector),
                "embedding_vector": embedding_vector[:10],  # Show first 10 dimensions
                "embedding_norm": sum(x*x for x in embedding_vector) ** 0.5,  # L2 norm
                "metadata": chunk.metadata
            }
            chunk_analysis.append(chunk_info)

        return {
            "file_path": file_path,
            "original_length": len(document.page_content),
            "original_word_count": len(document.page_content.split()),
            "total_chunks": len(chunks),
            "chunk_size": self.chunk_size,
            "chunk_overlap": self.chunk_overlap,
            "embedding_model": self.embedding_model,
            "chunks": chunk_analysis
        }

    def get_collection_info(self) -> dict:
        """
        Get information about the vector store collection

        Returns:
            Dictionary with collection information
        """
        if self.vectorstore is None:
            return {"status": "No vector store initialized"}

        try:
            collection = self.vectorstore._collection
            count = collection.count()
            return {
                "status": "Vector store active",
                "document_count": count,
                "persist_directory": self.persist_directory
            }
        except Exception as e:
            return {"status": f"Error getting collection info: {e}"}

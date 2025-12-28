"""
Corrective RAG System Implementation
This system evaluates retrieved documents and uses web search as fallback
"""

import os
from typing import List, Optional, Dict, Tuple
from pathlib import Path
from enum import Enum

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader, DirectoryLoader
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.schema import Document
from langchain.prompts import PromptTemplate
from langchain_community.tools import DuckDuckGoSearchResults
from langchain.chains import LLMChain


class RelevanceGrade(Enum):
    """Document relevance grades"""
    RELEVANT = "relevant"
    PARTIALLY_RELEVANT = "partially_relevant"
    NOT_RELEVANT = "not_relevant"


class CorrectiveRAGSystem:
    """
    A Corrective RAG system that:
    1. Retrieves documents from vector store
    2. Grades relevance of retrieved documents
    3. Filters irrelevant documents
    4. Falls back to web search if needed
    5. Generates answer with corrected information
    """
    
    def __init__(
        self,
        openai_api_key: Optional[str] = None,
        embedding_model: str = "text-embedding-3-large",
        llm_model: str = "gpt-3.5-turbo",
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        persist_directory: str = "./chroma_db",
        relevance_threshold: Optional[float] = 0.7,
        min_relevant_docs: Optional[int] = None,
        use_web_search: bool = True
    ):
        """
        Initialize the Corrective RAG system

        Args:
            openai_api_key: OpenAI API key
            embedding_model: OpenAI embedding model name
            llm_model: OpenAI model name
            chunk_size: Size of text chunks
            chunk_overlap: Overlap between chunks
            persist_directory: Directory to persist ChromaDB
            relevance_threshold: Fixed threshold for document relevance (0-1). 
                                If None, will use dynamic threshold based on min_relevant_docs.
            min_relevant_docs: Minimum number of relevant documents required.
                              If set, threshold will be calculated as min_relevant_docs / k.
                              If None, will use fixed relevance_threshold.
            use_web_search: Whether to use web search as fallback
        """
        self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        self.embedding_model = embedding_model
        self.llm_model = llm_model
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.persist_directory = persist_directory
        self.relevance_threshold = relevance_threshold
        self.min_relevant_docs = min_relevant_docs
        self.use_web_search = use_web_search
        
        # Initialize components
        if self.openai_api_key:
            self.embeddings = OpenAIEmbeddings(
                openai_api_key=self.openai_api_key,
                model=self.embedding_model
            )
            self.llm = ChatOpenAI(
                openai_api_key=self.openai_api_key,
                model_name=self.llm_model,
                temperature=0
            )
        else:
            print("Warning: No OpenAI API key provided. System functionality will be limited.")
            self.embeddings = None
            self.llm = None
        
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len,
        )
        
        self.vectorstore = None
        
        # Initialize web search tool
        if self.use_web_search:
            try:
                self.web_search = DuckDuckGoSearchResults(num_results=3)
            except Exception as e:
                print(f"Warning: Could not initialize web search: {e}")
                self.web_search = None
        else:
            self.web_search = None
        
        # Setup relevance grader prompt
        self._setup_relevance_grader()
        
        # Setup answer generation prompt
        self._setup_answer_generator()
    
    def _calculate_threshold(self, k: int) -> float:
        """
        Calculate the relevance threshold dynamically based on k (number of retrieved documents)
        
        Args:
            k: Number of documents retrieved
            
        Returns:
            Threshold value (0-1)
        """
        if self.min_relevant_docs is not None:
            # Dynamic threshold: ensure we have at least min_relevant_docs relevant documents
            # Threshold = min_relevant_docs / k, capped at 1.0
            dynamic_threshold = min(1.0, self.min_relevant_docs / k) if k > 0 else 1.0
            return dynamic_threshold
        else:
            # Use fixed threshold if min_relevant_docs is not set
            return self.relevance_threshold if self.relevance_threshold is not None else 0.7
    
    def _setup_relevance_grader(self):
        """Setup the relevance grading chain"""
        if self.llm is None:
            self.relevance_grader = None
            return
        
        relevance_prompt = PromptTemplate(
            template="""You are a grader assessing relevance of a retrieved document to a user question.
            
Here is the retrieved document:
{document}

Here is the user question:
{question}

IMPORTANT: Be precise about what the question is asking for:
- If the question asks about a BUILT-IN hardware feature (e.g., "built-in projector", "máy chiếu tích hợp"), documents about screen mirroring/projection via external devices are NOT relevant
- Distinguish between what iPhone HAS (built-in hardware) vs what iPhone CAN DO (via external devices/software)
- Example: Question "How to use built-in projector?" vs Document "How to mirror screen to external projector" → NOT relevant (different things)

If the document directly addresses what the question is asking for, grade it as relevant.
Give a binary score 'yes' or 'no' to indicate whether the document is relevant to the question.

Provide the score as a JSON with a single key 'score' and no other text or explanation.

Example response:
{{"score": "yes"}}

Your response:""",
            input_variables=["document", "question"]
        )
        
        self.relevance_grader = LLMChain(
            llm=self.llm,
            prompt=relevance_prompt
        )
    
    def _setup_answer_generator(self):
        """Setup the answer generation chain"""
        if self.llm is None:
            self.answer_generator = None
            return
        
        answer_prompt = PromptTemplate(
            template="""You are an assistant for question-answering tasks.
Use the following pieces of retrieved context to answer the question comprehensively and clearly.
If you don't know the answer, just say that you don't know.

INSTRUCTIONS:
- Provide a detailed and informative answer (4-6 sentences)
- Include specific details about the feature: what it is, how it works, where it's located, what models have it
- Be clear and precise in your explanation
- Answer in Vietnamese

CRITICAL RULES:
1. When answering about hardware features (like buttons, ports, switches), be precise about whether they are physical hardware components or software UI elements.

2. IMPORTANT - Distinguishing non-existent features:
   - If the question asks about a built-in hardware feature that doesn't exist (e.g., "built-in projector", "máy chiếu tích hợp"), you MUST clarify that iPhone does NOT have this feature
   - Do NOT confuse "screen mirroring/projection via AirPlay" with "built-in projector hardware"
   - Example: If asked "How to use built-in projector on iPhone?", answer: "iPhone does NOT have a built-in projector. However, you can use AirPlay to mirror your screen to external projectors or TVs."
   - Always distinguish between what iPhone CAN do (via external devices) vs what iPhone HAS (built-in hardware)

3. SPECIFIC RULES FOR ACTION BUTTON:
   - Action Button on iPhone 15 Pro/Pro Max is a PHYSICAL HARDWARE BUTTON (not a software UI element)
   - It replaced the Mute Switch (Cần gạt rung/chuông) on iPhone 15 Pro models
   - It is located on the left side of the device, similar to where the Mute Switch was
   - Users can customize what action the button performs (camera, flashlight, voice memo, etc.)

Question: {question}

Context: {context}

Answer:""",
            input_variables=["question", "context"]
        )
        
        self.answer_generator = LLMChain(
            llm=self.llm,
            prompt=answer_prompt
        )
    
    def load_documents_from_directory(self, directory_path: str, glob_pattern: str = "**/*.txt") -> List[Document]:
        """Load documents from a directory"""
        loader = DirectoryLoader(
            directory_path,
            glob=glob_pattern,
            loader_cls=TextLoader
        )
        documents = loader.load()
        return documents
    
    def load_documents_from_files(self, file_paths: List[str]) -> List[Document]:
        """Load documents from specific files"""
        documents = []
        for file_path in file_paths:
            loader = TextLoader(file_path)
            docs = loader.load()
            documents.extend(docs)
        return documents
    
    def add_documents(self, documents: List[Document]) -> None:
        """Add documents to the vector store"""
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
        """Load existing vector store from disk"""
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
    
    def grade_document_relevance(self, document: Document, question: str) -> Tuple[bool, str]:
        """
        Grade the relevance of a document to a question
        
        Returns:
            Tuple of (is_relevant: bool, raw_response: str)
        """
        if self.relevance_grader is None:
            # If no grader available, assume relevant
            return True, "no_grader"
        
        try:
            response = self.relevance_grader.run(
                document=document.page_content,
                question=question
            )
            
            # Parse response
            import json
            response = response.strip()
            
            # Try to extract JSON
            if "{" in response and "}" in response:
                start = response.find("{")
                end = response.rfind("}") + 1
                json_str = response[start:end]
                parsed = json.loads(json_str)
                score = parsed.get("score", "").lower()
                is_relevant = score == "yes"
            else:
                # Fallback: check if response contains "yes"
                is_relevant = "yes" in response.lower()
            
            return is_relevant, response
            
        except Exception as e:
            print(f"Error grading document: {e}")
            # On error, assume relevant to be safe
            return True, f"error: {e}"
    
    def retrieve_documents(self, question: str, k: int = 4) -> List[Document]:
        """Retrieve documents from vector store"""
        if self.vectorstore is None:
            raise ValueError("Vector store not initialized. Please add documents first.")
        
        return self.vectorstore.similarity_search(question, k=k)
    
    def web_search_fallback(self, question: str) -> str:
        """Perform web search as fallback"""
        if self.web_search is None:
            return "Web search not available."
        
        try:
            results = self.web_search.run(question)
            return results
        except Exception as e:
            print(f"Web search error: {e}")
            return f"Web search failed: {e}"
    
    def query(self, question: str, k: int = 4, return_diagnostics: bool = False) -> dict:
        """
        Query the Corrective RAG system with self-correction
        
        Args:
            question: Question to ask
            k: Number of documents to retrieve
            return_diagnostics: Whether to return diagnostic information
            
        Returns:
            Dictionary containing answer and optional diagnostics
        """
        if self.vectorstore is None:
            raise ValueError("Vector store not initialized. Please add documents first.")
        
        if self.llm is None:
            raise ValueError("LLM not initialized. Please provide OpenAI API key.")
        
        # Step 1: Retrieve documents
        retrieved_docs = self.retrieve_documents(question, k=k)
        
        # Step 2: Grade document relevance
        relevant_docs = []
        irrelevant_docs = []
        grading_results = []
        
        for doc in retrieved_docs:
            is_relevant, grade_response = self.grade_document_relevance(doc, question)
            
            if is_relevant:
                relevant_docs.append(doc)
            else:
                irrelevant_docs.append(doc)
            
            grading_results.append({
                "content_preview": doc.page_content[:100] + "...",
                "is_relevant": is_relevant,
                "grade_response": grade_response
            })
        
        # Step 3: Decide on correction strategy
        relevance_ratio = len(relevant_docs) / len(retrieved_docs) if retrieved_docs else 0
        
        # Calculate dynamic threshold based on k
        current_threshold = self._calculate_threshold(k)
        
        context_parts = []
        used_web_search = False
        web_search_results = None
        
        # If we have relevant documents, use them
        if relevant_docs:
            context_parts.extend([doc.page_content for doc in relevant_docs])
        
        # If relevance is low, add web search results
        if relevance_ratio < current_threshold and self.use_web_search:
            web_search_results = self.web_search_fallback(question)
            if web_search_results and "failed" not in web_search_results.lower():
                context_parts.append(f"\n\nAdditional web search results:\n{web_search_results}")
                used_web_search = True
        
        # Step 4: Generate answer
        if not context_parts:
            answer = "I don't have enough relevant information to answer this question."
        else:
            context = "\n\n".join(context_parts)
            answer = self.answer_generator.run(
                question=question,
                context=context
            )
        
        # Prepare response
        result = {
            "answer": answer,
            "source_documents": relevant_docs
        }
        
        if return_diagnostics:
            result["diagnostics"] = {
                "total_retrieved": len(retrieved_docs),
                "relevant_count": len(relevant_docs),
                "irrelevant_count": len(irrelevant_docs),
                "relevance_ratio": relevance_ratio,
                "threshold_used": current_threshold,
                "threshold_type": "dynamic" if self.min_relevant_docs is not None else "fixed",
                "min_relevant_docs": self.min_relevant_docs,
                "used_web_search": used_web_search,
                "web_search_results": web_search_results,
                "grading_results": grading_results
            }
        
        return result
    
    def similarity_search(self, query: str, k: int = 4) -> List[Document]:
        """Perform similarity search without LLM"""
        if self.vectorstore is None:
            raise ValueError("Vector store not initialized. Please add documents first.")
        
        return self.vectorstore.similarity_search(query, k=k)
    
    def analyze_document_chunks(self, file_path: str) -> dict:
        """Analyze how a document is split into chunks and show embeddings"""
        if self.embeddings is None:
            raise ValueError("Embeddings not initialized. Please provide OpenAI API key.")

        # Load the document
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
        """Get information about the vector store collection"""
        if self.vectorstore is None:
            return {"status": "No vector store initialized"}

        try:
            collection = self.vectorstore._collection
            count = collection.count()
            return {
                "status": "Vector store active",
                "document_count": count,
                "persist_directory": self.persist_directory,
                "system_type": "Corrective RAG",
                "relevance_threshold": self.relevance_threshold,
                "min_relevant_docs": self.min_relevant_docs,
                "threshold_mode": "dynamic" if self.min_relevant_docs is not None else "fixed",
                "web_search_enabled": self.use_web_search
            }
        except Exception as e:
            return {"status": f"Error getting collection info: {e}"}


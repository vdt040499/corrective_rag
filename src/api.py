"""
FastAPI application for Corrective RAG system
"""

import os
from typing import List, Optional
from pathlib import Path

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import tempfile

from .corrective_rag_system import CorrectiveRAGSystem


# Pydantic models
class QueryRequest(BaseModel):
    question: str
    k: Optional[int] = 4
    return_diagnostics: Optional[bool] = False


class QueryResponse(BaseModel):
    answer: str
    sources: List[str]
    diagnostics: Optional[dict] = None


class SearchRequest(BaseModel):
    query: str
    k: Optional[int] = 4


class SearchResponse(BaseModel):
    documents: List[dict]


class StatusResponse(BaseModel):
    status: str
    document_count: Optional[int] = None
    persist_directory: Optional[str] = None
    system_type: Optional[str] = None
    relevance_threshold: Optional[float] = None
    web_search_enabled: Optional[bool] = None


# Initialize FastAPI app
app = FastAPI(
    title="Corrective RAG System API",
    description="A RESTful API for Corrective Retrieval-Augmented Generation system with self-correction and web search",
    version="2.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Corrective RAG system
rag_system = CorrectiveRAGSystem(
    relevance_threshold=0.6,  # Adjust threshold as needed
    use_web_search=True
)

# Load existing vector store if available
rag_system.load_vectorstore()


@app.get("/", response_model=dict)
async def root():
    """Root endpoint"""
    return {
        "message": "Corrective RAG System API",
        "version": "2.0.0",
        "description": "Self-correcting RAG with relevance grading and web search fallback",
        "endpoints": {
            "status": "/status",
            "upload": "/upload",
            "query": "/query (supports diagnostics)",
            "search": "/search"
        }
    }


@app.get("/status", response_model=StatusResponse)
async def get_status():
    """Get system status"""
    info = rag_system.get_collection_info()
    return StatusResponse(**info)


@app.post("/upload/files")
async def upload_files(files: List[UploadFile] = File(...)):
    """Upload and process multiple files"""
    try:
        documents = []
        temp_files = []
        
        for file in files:
            # Save uploaded file temporarily
            with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.txt') as temp_file:
                content = await file.read()
                temp_file.write(content)
                temp_files.append(temp_file.name)
        
        # Load documents from temporary files
        documents = rag_system.load_documents_from_files(temp_files)
        
        # Add documents to vector store
        rag_system.add_documents(documents)
        
        # Clean up temporary files
        for temp_file in temp_files:
            os.unlink(temp_file)
        
        return {
            "message": f"Successfully processed {len(files)} files",
            "documents_added": len(documents)
        }
    
    except Exception as e:
        # Clean up temporary files in case of error
        for temp_file in temp_files:
            try:
                os.unlink(temp_file)
            except:
                pass
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/upload/directory")
async def upload_directory(directory_path: str = Form(...), glob_pattern: str = Form("**/*.txt")):
    """Process documents from a directory"""
    try:
        if not Path(directory_path).exists():
            raise HTTPException(status_code=404, detail="Directory not found")
        
        # Load documents from directory
        documents = rag_system.load_documents_from_directory(directory_path, glob_pattern)
        
        if not documents:
            raise HTTPException(status_code=404, detail="No documents found in directory")
        
        # Add documents to vector store
        rag_system.add_documents(documents)
        
        return {
            "message": f"Successfully processed directory: {directory_path}",
            "documents_added": len(documents)
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/query", response_model=QueryResponse)
async def query_documents(request: QueryRequest):
    """Query the Corrective RAG system with self-correction"""
    try:
        if rag_system.llm is None:
            raise HTTPException(
                status_code=400, 
                detail="QA system not available. Please ensure OpenAI API key is set and documents are uploaded."
            )
        
        result = rag_system.query(
            request.question, 
            k=request.k,
            return_diagnostics=request.return_diagnostics
        )
        
        # Extract source information
        sources = []
        for doc in result["source_documents"]:
            source_info = f"Source: {doc.metadata.get('source', 'Unknown')}"
            if 'page' in doc.metadata:
                source_info += f", Page: {doc.metadata['page']}"
            sources.append(source_info)
        
        response_data = {
            "answer": result["answer"],
            "sources": sources
        }
        
        # Add diagnostics if requested
        if request.return_diagnostics and "diagnostics" in result:
            response_data["diagnostics"] = result["diagnostics"]
        
        return QueryResponse(**response_data)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/search", response_model=SearchResponse)
async def search_documents(request: SearchRequest):
    """Search for similar documents"""
    try:
        if rag_system.vectorstore is None:
            raise HTTPException(
                status_code=400,
                detail="Vector store not initialized. Please upload documents first."
            )
        
        documents = rag_system.similarity_search(request.query, k=request.k)
        
        # Format documents for response
        formatted_docs = []
        for doc in documents:
            formatted_docs.append({
                "content": doc.page_content,
                "metadata": doc.metadata
            })
        
        return SearchResponse(documents=formatted_docs)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/reset")
async def reset_system():
    """Reset the vector store"""
    try:
        # Remove persist directory if it exists
        if Path(rag_system.persist_directory).exists():
            import shutil
            shutil.rmtree(rag_system.persist_directory)
        
        # Reset system components
        rag_system.vectorstore = None
        
        return {"message": "Corrective RAG system reset successfully"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

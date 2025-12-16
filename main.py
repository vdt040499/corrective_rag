"""
Main entry point for the RAG system
"""

import os
import sys
from pathlib import Path

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.api import app

if __name__ == "__main__":
    import uvicorn

    # Get configuration from environment variables
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    reload = os.getenv("RELOAD", "true").lower() == "true"

    print(f"Starting RAG System API on {host}:{port}")
    print("API Documentation available at: http://localhost:8000/docs")

    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=reload
    )

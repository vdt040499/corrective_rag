#!/usr/bin/env python3
"""
Installation Test Script for Corrective RAG System
Run this to verify your setup is correct
"""

import os
import sys
from pathlib import Path

# Colors for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


def print_header(text):
    """Print a header"""
    print(f"\n{Colors.CYAN}{Colors.BOLD}{'='*70}{Colors.RESET}")
    print(f"{Colors.CYAN}{Colors.BOLD}{text.center(70)}{Colors.RESET}")
    print(f"{Colors.CYAN}{Colors.BOLD}{'='*70}{Colors.RESET}\n")


def print_success(text):
    """Print success message"""
    print(f"{Colors.GREEN}✓ {text}{Colors.RESET}")


def print_error(text):
    """Print error message"""
    print(f"{Colors.RED}✗ {text}{Colors.RESET}")


def print_warning(text):
    """Print warning message"""
    print(f"{Colors.YELLOW}⚠ {text}{Colors.RESET}")


def print_info(text):
    """Print info message"""
    print(f"{Colors.BLUE}ℹ {text}{Colors.RESET}")


def test_python_version():
    """Test Python version"""
    print_info("Testing Python version...")
    version = sys.version_info
    
    if version.major >= 3 and version.minor >= 12:
        print_success(f"Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print_error(f"Python {version.major}.{version.minor}.{version.micro} (requires >=3.12)")
        return False


def test_imports():
    """Test if all required packages can be imported"""
    print_info("Testing package imports...")
    
    packages = [
        ("langchain", "LangChain"),
        ("langchain_openai", "LangChain OpenAI"),
        ("langchain_community", "LangChain Community"),
        ("chromadb", "ChromaDB"),
        ("fastapi", "FastAPI"),
        ("typer", "Typer"),
        ("rich", "Rich"),
        ("duckduckgo_search", "DuckDuckGo Search"),
    ]
    
    all_ok = True
    for package, name in packages:
        try:
            __import__(package)
            print_success(f"{name} installed")
        except ImportError:
            print_error(f"{name} NOT installed")
            all_ok = False
    
    return all_ok


def test_openai_key():
    """Test if OpenAI API key is set"""
    print_info("Testing OpenAI API key...")
    
    api_key = os.getenv("OPENAI_API_KEY")
    
    if api_key:
        # Don't print the full key for security
        masked_key = api_key[:7] + "..." + api_key[-4:] if len(api_key) > 11 else "***"
        print_success(f"OpenAI API key found: {masked_key}")
        return True
    else:
        print_error("OpenAI API key NOT found")
        print_warning("Set it with: export OPENAI_API_KEY='your-key-here'")
        return False


def test_corrective_rag_import():
    """Test if CorrectiveRAGSystem can be imported"""
    print_info("Testing Corrective RAG System import...")
    
    try:
        sys.path.insert(0, str(Path(__file__).parent))
        from src.corrective_rag_system import CorrectiveRAGSystem
        print_success("CorrectiveRAGSystem can be imported")
        return True
    except Exception as e:
        print_error(f"CorrectiveRAGSystem import failed: {e}")
        return False


def test_system_initialization():
    """Test if system can be initialized"""
    print_info("Testing system initialization...")
    
    try:
        sys.path.insert(0, str(Path(__file__).parent))
        from src.corrective_rag_system import CorrectiveRAGSystem
        
        rag = CorrectiveRAGSystem(
            relevance_threshold=0.6,
            use_web_search=True
        )
        print_success("System initialized successfully")
        
        # Test info
        info = rag.get_collection_info()
        print_success(f"System type: {info.get('system_type', 'Corrective RAG')}")
        
        return True
    except Exception as e:
        print_error(f"System initialization failed: {e}")
        return False


def test_vector_store():
    """Test if vector store exists"""
    print_info("Testing vector store...")
    
    persist_dir = Path("./chroma_db")
    
    if persist_dir.exists():
        print_success(f"Vector store found at: {persist_dir}")
        
        # Try to count documents
        try:
            sys.path.insert(0, str(Path(__file__).parent))
            from src.corrective_rag_system import CorrectiveRAGSystem
            
            rag = CorrectiveRAGSystem()
            if rag.load_vectorstore():
                info = rag.get_collection_info()
                count = info.get("document_count", 0)
                print_success(f"Documents in store: {count}")
                return True
        except Exception as e:
            print_warning(f"Could not load vector store: {e}")
            return False
    else:
        print_warning("No vector store found (this is OK for new installations)")
        print_info("Add documents with: uv run python cli.py add-directory examples/sample_documents")
        return None  # Not an error for new installations


def test_web_search():
    """Test if web search is available"""
    print_info("Testing web search capability...")
    
    try:
        from langchain_community.tools import DuckDuckGoSearchResults
        search = DuckDuckGoSearchResults(num_results=1)
        print_success("DuckDuckGo search available")
        return True
    except Exception as e:
        print_error(f"Web search not available: {e}")
        return False


def test_cli():
    """Test if CLI can be run"""
    print_info("Testing CLI availability...")
    
    cli_path = Path(__file__).parent / "cli.py"
    
    if cli_path.exists():
        print_success(f"CLI script found: {cli_path}")
        return True
    else:
        print_error("CLI script not found")
        return False


def test_api():
    """Test if API can be imported"""
    print_info("Testing API availability...")
    
    try:
        sys.path.insert(0, str(Path(__file__).parent))
        from src.api import app
        print_success("API module can be imported")
        return True
    except Exception as e:
        print_error(f"API import failed: {e}")
        return False


def test_sample_documents():
    """Test if sample documents exist"""
    print_info("Testing sample documents...")
    
    sample_dir = Path(__file__).parent / "examples" / "sample_documents"
    
    if sample_dir.exists():
        files = list(sample_dir.glob("*.txt"))
        if files:
            print_success(f"Sample documents found: {len(files)} files")
            return True
        else:
            print_warning("Sample documents directory exists but is empty")
            return False
    else:
        print_warning("Sample documents directory not found")
        return False


def main():
    """Run all tests"""
    print_header("Corrective RAG System - Installation Test")
    
    print(f"{Colors.MAGENTA}This script will verify your installation is correct{Colors.RESET}\n")
    
    results = []
    
    # Run all tests
    tests = [
        ("Python Version", test_python_version),
        ("Package Imports", test_imports),
        ("OpenAI API Key", test_openai_key),
        ("Corrective RAG Import", test_corrective_rag_import),
        ("System Initialization", test_system_initialization),
        ("Vector Store", test_vector_store),
        ("Web Search", test_web_search),
        ("CLI Availability", test_cli),
        ("API Availability", test_api),
        ("Sample Documents", test_sample_documents),
    ]
    
    for test_name, test_func in tests:
        print(f"\n{Colors.BOLD}Testing: {test_name}{Colors.RESET}")
        result = test_func()
        results.append((test_name, result))
    
    # Summary
    print_header("Test Summary")
    
    passed = sum(1 for _, r in results if r is True)
    failed = sum(1 for _, r in results if r is False)
    warnings = sum(1 for _, r in results if r is None)
    total = len(results)
    
    for test_name, result in results:
        if result is True:
            print_success(f"{test_name}")
        elif result is False:
            print_error(f"{test_name}")
        else:
            print_warning(f"{test_name} (optional)")
    
    print(f"\n{Colors.BOLD}Results:{Colors.RESET}")
    print(f"  {Colors.GREEN}Passed: {passed}/{total}{Colors.RESET}")
    print(f"  {Colors.RED}Failed: {failed}/{total}{Colors.RESET}")
    print(f"  {Colors.YELLOW}Warnings: {warnings}/{total}{Colors.RESET}")
    
    # Final status
    if failed == 0:
        print_header("Installation Status: SUCCESS ✓")
        print(f"{Colors.GREEN}Your Corrective RAG system is ready to use!{Colors.RESET}\n")
        
        print(f"{Colors.CYAN}Next steps:{Colors.RESET}")
        print("  1. Add documents: uv run python cli.py add-directory examples/sample_documents")
        print("  2. Try a query:   uv run python cli.py query 'What is Python?' --diagnostics")
        print("  3. Run demo:      uv run python examples/demo_corrective_rag.py")
        print("  4. Start API:     uv run python main.py")
        
        return 0
    else:
        print_header("Installation Status: ISSUES FOUND ✗")
        print(f"{Colors.RED}Please fix the errors above and run this test again{Colors.RESET}\n")
        
        print(f"{Colors.CYAN}Common fixes:{Colors.RESET}")
        print("  • Install dependencies: uv sync")
        print("  • Set API key: export OPENAI_API_KEY='your-key-here'")
        print("  • Check Python version: python --version (needs >=3.12)")
        
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)


"""
Demo: Corrective RAG System
This demonstrates the self-correction capabilities of the Corrective RAG system
"""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.corrective_rag_system import CorrectiveRAGSystem
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()


def print_section(title: str):
    """Print a section header"""
    console.print(f"\n[bold cyan]{'=' * 80}[/bold cyan]")
    console.print(f"[bold cyan]{title}[/bold cyan]")
    console.print(f"[bold cyan]{'=' * 80}[/bold cyan]\n")


def print_diagnostics(diagnostics: dict):
    """Pretty print diagnostics information"""
    table = Table(title="🔍 Corrective RAG Diagnostics")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="yellow")
    
    table.add_row("Total Retrieved", str(diagnostics["total_retrieved"]))
    table.add_row("Relevant Documents", f"[green]{diagnostics['relevant_count']}[/green]")
    table.add_row("Irrelevant Documents", f"[red]{diagnostics['irrelevant_count']}[/red]")
    table.add_row("Relevance Ratio", f"{diagnostics['relevance_ratio']:.2%}")
    table.add_row("Used Web Search", "✓ Yes" if diagnostics["used_web_search"] else "✗ No")
    
    console.print(table)
    
    # Show grading results
    if diagnostics["grading_results"]:
        console.print("\n[bold]Document Grading:[/bold]")
        for i, grade in enumerate(diagnostics["grading_results"], 1):
            icon = "✓" if grade["is_relevant"] else "✗"
            color = "green" if grade["is_relevant"] else "red"
            console.print(f"  [{color}]{icon}[/{color}] Doc {i}: {grade['content_preview']}")


def demo_basic_query():
    """Demo 1: Basic query with diagnostics"""
    print_section("Demo 1: Basic Query with Self-Correction")
    
    # Initialize system
    rag = CorrectiveRAGSystem(
        relevance_threshold=0.6,
        use_web_search=True
    )
    
    # Load or create vector store
    if not rag.load_vectorstore():
        console.print("[yellow]No existing vector store found. Please add documents first.[/yellow]")
        console.print("[yellow]Run: uv run python cli.py add-directory examples/sample_documents[/yellow]")
        return
    
    # Query with diagnostics
    question = "What is Python programming?"
    console.print(f"[bold]Question:[/bold] {question}\n")
    
    with console.status("[bold green]Processing query with self-correction..."):
        result = rag.query(question, k=4, return_diagnostics=True)
    
    # Display answer
    console.print(Panel(result["answer"], title="Answer", border_style="green"))
    
    # Display diagnostics
    if "diagnostics" in result:
        console.print()
        print_diagnostics(result["diagnostics"])
    
    # Display sources
    if result["source_documents"]:
        console.print("\n[bold]Relevant Sources Used:[/bold]")
        for i, doc in enumerate(result["source_documents"], 1):
            source = doc.metadata.get('source', 'Unknown')
            preview = doc.page_content[:150] + "..."
            console.print(f"  {i}. [dim]{source}[/dim]")
            console.print(f"     {preview}\n")


def demo_web_search_fallback():
    """Demo 2: Query that triggers web search"""
    print_section("Demo 2: Web Search Fallback")
    
    rag = CorrectiveRAGSystem(
        relevance_threshold=0.6,
        use_web_search=True
    )
    
    if not rag.load_vectorstore():
        console.print("[yellow]No vector store found.[/yellow]")
        return
    
    # Query about something likely not in local docs
    question = "What are the latest developments in quantum computing in 2024?"
    console.print(f"[bold]Question:[/bold] {question}")
    console.print("[dim]This query is likely to trigger web search fallback[/dim]\n")
    
    with console.status("[bold green]Processing with possible web search..."):
        result = rag.query(question, k=4, return_diagnostics=True)
    
    console.print(Panel(result["answer"], title="Answer", border_style="green"))
    
    if "diagnostics" in result:
        console.print()
        print_diagnostics(result["diagnostics"])
        
        if result["diagnostics"]["used_web_search"]:
            console.print("\n[bold yellow]Web search was used to enhance the answer![/bold yellow]")


def demo_relevance_grading():
    """Demo 3: Show relevance grading in action"""
    print_section("Demo 3: Relevance Grading Comparison")
    
    # Test with different thresholds
    thresholds = [0.3, 0.6, 0.9]
    question = "Explain machine learning concepts"
    
    for threshold in thresholds:
        console.print(f"\n[bold cyan]Testing with relevance threshold: {threshold}[/bold cyan]")
        
        rag = CorrectiveRAGSystem(
            relevance_threshold=threshold,
            use_web_search=True
        )
        
        if not rag.load_vectorstore():
            console.print("[yellow]No vector store found.[/yellow]")
            return
        
        result = rag.query(question, k=4, return_diagnostics=True)
        
        if "diagnostics" in result:
            diag = result["diagnostics"]
            console.print(f"  Relevant: {diag['relevant_count']}/{diag['total_retrieved']}")
            console.print(f"  Used Web Search: {'Yes' if diag['used_web_search'] else 'No'}")


def demo_similarity_search():
    """Demo 4: Basic similarity search"""
    print_section("Demo 4: Similarity Search (No LLM)")
    
    rag = CorrectiveRAGSystem()
    
    if not rag.load_vectorstore():
        console.print("[yellow]No vector store found.[/yellow]")
        return
    
    query = "programming languages"
    console.print(f"[bold]Search Query:[/bold] {query}\n")
    
    docs = rag.similarity_search(query, k=3)
    
    console.print(f"[bold]Found {len(docs)} similar documents:[/bold]\n")
    for i, doc in enumerate(docs, 1):
        source = doc.metadata.get('source', 'Unknown')
        preview = doc.page_content[:200] + "..."
        console.print(Panel(
            preview,
            title=f"Document {i} - {Path(source).name}",
            border_style="blue"
        ))


def demo_custom_configuration():
    """Demo 5: Custom configuration"""
    print_section("Demo 5: Custom Configuration")
    
    # Create system with custom settings
    rag = CorrectiveRAGSystem(
        embedding_model="text-embedding-3-large",
        llm_model="gpt-3.5-turbo",
        chunk_size=800,
        chunk_overlap=150,
        relevance_threshold=0.7,
        use_web_search=True
    )
    
    info = rag.get_collection_info()
    
    table = Table(title="System Configuration")
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="green")
    
    table.add_row("System Type", info.get("system_type", "Corrective RAG"))
    table.add_row("Embedding Model", rag.embedding_model)
    table.add_row("LLM Model", rag.llm_model)
    table.add_row("Chunk Size", str(rag.chunk_size))
    table.add_row("Chunk Overlap", str(rag.chunk_overlap))
    table.add_row("Relevance Threshold", str(info.get("relevance_threshold", "N/A")))
    table.add_row("Web Search", str(info.get("web_search_enabled", "N/A")))
    
    console.print(table)


def main():
    """Run all demos"""
    console.print("[bold magenta]Corrective RAG System Demo[/bold magenta]")
    console.print("[dim]Demonstrating self-correction, relevance grading, and web search fallback[/dim]")
    
    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        console.print("\n[red]Error: OPENAI_API_KEY not found in environment variables[/red]")
        console.print("[yellow]Please set your OpenAI API key:[/yellow]")
        console.print("[yellow]export OPENAI_API_KEY='your-api-key-here'[/yellow]")
        return
    
    try:
        # Run demos
        demo_basic_query()
        input("\nPress Enter to continue to next demo...")
        
        demo_web_search_fallback()
        input("\nPress Enter to continue to next demo...")
        
        demo_relevance_grading()
        input("\nPress Enter to continue to next demo...")
        
        demo_similarity_search()
        input("\nPress Enter to continue to next demo...")
        
        demo_custom_configuration()
        
        print_section("Demo Complete!")
        console.print("[green]All demos completed successfully![/green]")
        console.print("\n[bold]Try it yourself:[/bold]")
        console.print("  uv run python cli.py query 'Your question here' --diagnostics")
        console.print("  uv run python cli.py interactive")
        
    except KeyboardInterrupt:
        console.print("\n[yellow]Demo interrupted by user[/yellow]")
    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]")


if __name__ == "__main__":
    main()


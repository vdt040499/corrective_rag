"""
Command Line Interface for Corrective RAG system
"""

import os
import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.tree import Tree
from rich import print as rprint

from .corrective_rag_system import CorrectiveRAGSystem

app = typer.Typer(help="Corrective RAG System Command Line Interface")
console = Console()


def get_rag_system() -> CorrectiveRAGSystem:
    """Initialize and return Corrective RAG system"""
    return CorrectiveRAGSystem(
        relevance_threshold=0.6,
        use_web_search=True
    )


@app.command()
def status():
    """Show system status"""
    rag = get_rag_system()
    rag.load_vectorstore()
    
    info = rag.get_collection_info()
    
    table = Table(title="Corrective RAG System Status")
    table.add_column("Property", style="cyan")
    table.add_column("Value", style="green")
    
    table.add_row("System Type", info.get("system_type", "Corrective RAG"))
    table.add_row("Status", info.get("status", "Unknown"))
    table.add_row("Document Count", str(info.get("document_count", "N/A")))
    table.add_row("Persist Directory", info.get("persist_directory", "N/A"))
    table.add_row("Relevance Threshold", str(info.get("relevance_threshold", "N/A")))
    table.add_row("Web Search Enabled", str(info.get("web_search_enabled", "N/A")))
    table.add_row("OpenAI API Key", "Set" if os.getenv("OPENAI_API_KEY") else "Not Set")
    
    console.print(table)


@app.command()
def add_directory(
    directory: str = typer.Argument(..., help="Directory path containing documents"),
    pattern: str = typer.Option("**/*.txt", help="File pattern to match"),
):
    """Add documents from a directory"""
    rag = get_rag_system()
    rag.load_vectorstore()
    
    if not Path(directory).exists():
        console.print(f"[red]Error: Directory '{directory}' does not exist[/red]")
        raise typer.Exit(1)
    
    try:
        with console.status("[bold green]Loading documents..."):
            documents = rag.load_documents_from_directory(directory, pattern)
        
        if not documents:
            console.print(f"[yellow]No documents found in '{directory}' with pattern '{pattern}'[/yellow]")
            return
        
        with console.status("[bold green]Adding documents to vector store..."):
            rag.add_documents(documents)
        
        console.print(f"[green]Successfully added {len(documents)} documents from '{directory}'[/green]")
        
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def add_files(
    files: list[str] = typer.Argument(..., help="File paths to add"),
):
    """Add specific files to the vector store"""
    rag = get_rag_system()
    rag.load_vectorstore()
    
    # Check if all files exist
    for file_path in files:
        if not Path(file_path).exists():
            console.print(f"[red]Error: File '{file_path}' does not exist[/red]")
            raise typer.Exit(1)
    
    try:
        with console.status("[bold green]Loading documents..."):
            documents = rag.load_documents_from_files(files)
        
        with console.status("[bold green]Adding documents to vector store..."):
            rag.add_documents(documents)
        
        console.print(f"[green]Successfully added {len(documents)} documents[/green]")
        
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def query(
    question: str = typer.Argument(..., help="Question to ask"),
    k: int = typer.Option(4, help="Number of documents to retrieve"),
    show_diagnostics: bool = typer.Option(False, "--diagnostics", help="Show diagnostic information"),
):
    """Query the Corrective RAG system with self-correction"""
    rag = get_rag_system()
    
    if not rag.load_vectorstore():
        console.print("[red]Error: No vector store found. Please add documents first.[/red]")
        raise typer.Exit(1)
    
    if not rag.openai_api_key:
        console.print("[red]Error: OpenAI API key not found. Please set OPENAI_API_KEY environment variable.[/red]")
        raise typer.Exit(1)
    
    try:
        with console.status("[bold green]Processing query with self-correction..."):
            result = rag.query(question, k=k, return_diagnostics=show_diagnostics)
        
        # Display answer
        console.print(Panel(result["answer"], title="Answer", border_style="green"))
        
        # Display diagnostics if requested
        if show_diagnostics and "diagnostics" in result:
            diag = result["diagnostics"]
            
            console.print("\n[bold magenta]🔍 Diagnostics Information:[/bold magenta]")
            
            diag_table = Table(title="Self-Correction Process")
            diag_table.add_column("Metric", style="cyan")
            diag_table.add_column("Value", style="yellow")
            
            diag_table.add_row("Total Retrieved", str(diag["total_retrieved"]))
            diag_table.add_row("Relevant Documents", f"[green]{diag['relevant_count']}[/green]")
            diag_table.add_row("Irrelevant Documents", f"[red]{diag['irrelevant_count']}[/red]")
            diag_table.add_row("Relevance Ratio", f"{diag['relevance_ratio']:.2%}")
            diag_table.add_row("Used Web Search", "✓ Yes" if diag["used_web_search"] else "✗ No")
            
            console.print(diag_table)
            
            # Show grading results
            if diag["grading_results"]:
                console.print("\n[bold cyan]Document Grading Results:[/bold cyan]")
                for i, grade in enumerate(diag["grading_results"], 1):
                    status_icon = "✓" if grade["is_relevant"] else "✗"
                    status_color = "green" if grade["is_relevant"] else "red"
                    console.print(f"  [{status_color}]{status_icon}[/{status_color}] Doc {i}: {grade['content_preview']}")
            
            # Show web search results if used
            if diag["used_web_search"] and diag["web_search_results"]:
                console.print("\n[bold yellow]Web Search Results Used:[/bold yellow]")
                console.print(Panel(str(diag["web_search_results"])[:500], border_style="yellow"))
        
        # Display sources
        if result["source_documents"]:
            console.print("\n[bold cyan]Relevant Sources:[/bold cyan]")
            for i, doc in enumerate(result["source_documents"], 1):
                source = doc.metadata.get('source', 'Unknown')
                content_preview = doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content
                console.print(f"[dim]{i}. {source}[/dim]")
                console.print(f"   {content_preview}\n")
        
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def search(
    query_text: str = typer.Argument(..., help="Search query"),
    k: int = typer.Option(4, help="Number of documents to return"),
):
    """Search for similar documents"""
    rag = get_rag_system()
    
    if not rag.load_vectorstore():
        console.print("[red]Error: No vector store found. Please add documents first.[/red]")
        raise typer.Exit(1)
    
    try:
        with console.status("[bold green]Searching..."):
            documents = rag.similarity_search(query_text, k=k)
        
        if not documents:
            console.print("[yellow]No similar documents found.[/yellow]")
            return
        
        console.print(f"[bold cyan]Found {len(documents)} similar documents:[/bold cyan]\n")
        
        for i, doc in enumerate(documents, 1):
            source = doc.metadata.get('source', 'Unknown')
            content_preview = doc.page_content[:300] + "..." if len(doc.page_content) > 300 else doc.page_content
            
            console.print(Panel(
                content_preview,
                title=f"Document {i} - {source}",
                border_style="blue"
            ))
            console.print()
        
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def reset():
    """Reset the vector store"""
    confirm = typer.confirm("Are you sure you want to reset the vector store? This will delete all stored documents.")
    
    if not confirm:
        console.print("[yellow]Reset cancelled.[/yellow]")
        return
    
    rag = get_rag_system()
    
    try:
        # Remove persist directory if it exists
        if Path(rag.persist_directory).exists():
            import shutil
            shutil.rmtree(rag.persist_directory)
        
        console.print("[green]Vector store reset successfully.[/green]")
        
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def analyze_chunks(
    file_path: str = typer.Argument(..., help="Path to the document file to analyze"),
    show_vectors: bool = typer.Option(False, "--show-vectors", help="Show full embedding vectors"),
    max_chunks: int = typer.Option(5, "--max-chunks", help="Maximum number of chunks to display")
):
    """Analyze how a document is split into chunks and show embeddings"""
    rag = get_rag_system()

    if not rag.openai_api_key:
        console.print("[red]Error: OpenAI API key not found. Please set OPENAI_API_KEY environment variable.[/red]")
        raise typer.Exit(1)

    if not Path(file_path).exists():
        console.print(f"[red]Error: File '{file_path}' does not exist[/red]")
        raise typer.Exit(1)

    try:
        with console.status("[bold green]Analyzing document chunks and generating embeddings..."):
            analysis = rag.analyze_document_chunks(file_path)

        # Display summary
        console.print(f"\n[bold cyan]Document Analysis: {analysis['file_path']}[/bold cyan]")

        summary_table = Table(title="Document Summary")
        summary_table.add_column("Property", style="cyan")
        summary_table.add_column("Value", style="green")

        summary_table.add_row("Original Length", f"{analysis['original_length']:,} characters")
        summary_table.add_row("Original Word Count", f"{analysis['original_word_count']:,} words")
        summary_table.add_row("Total Chunks", str(analysis['total_chunks']))
        summary_table.add_row("Chunk Size", str(analysis['chunk_size']))
        summary_table.add_row("Chunk Overlap", str(analysis['chunk_overlap']))
        summary_table.add_row("Embedding Model", analysis['embedding_model'])
        summary_table.add_row("Embedding Dimension", str(analysis['chunks'][0]['embedding_dimension']) if analysis['chunks'] else "N/A")

        console.print(summary_table)

        # Display chunks
        chunks_to_show = min(max_chunks, len(analysis['chunks']))
        console.print(f"\n[bold cyan]Showing {chunks_to_show} of {len(analysis['chunks'])} chunks:[/bold cyan]\n")

        for i, chunk in enumerate(analysis['chunks'][:chunks_to_show]):
            # Chunk header
            console.print(f"[bold yellow]Chunk {chunk['chunk_id']}[/bold yellow]")

            # Chunk details table
            chunk_table = Table(show_header=False, box=None)
            chunk_table.add_column("Property", style="dim")
            chunk_table.add_column("Value")

            chunk_table.add_row("Length:", f"{chunk['content_length']} characters")
            chunk_table.add_row("Words:", f"{chunk['word_count']} words")
            chunk_table.add_row("Embedding Norm:", f"{chunk['embedding_norm']:.4f}")

            console.print(chunk_table)

            # Content preview
            content_preview = chunk['content'][:200] + "..." if len(chunk['content']) > 200 else chunk['content']
            console.print(Panel(
                content_preview,
                title=f"Content Preview",
                border_style="blue"
            ))

            # Embedding vector preview
            if show_vectors:
                vector_str = ", ".join([f"{x:.4f}" for x in chunk['embedding_vector']])
                console.print(f"[dim]Embedding (first 10 dims): [{vector_str}, ...][/dim]")
            else:
                vector_preview = ", ".join([f"{x:.3f}" for x in chunk['embedding_vector'][:5]])
                console.print(f"[dim]Embedding preview: [{vector_preview}, ...][/dim]")

            console.print()  # Empty line

        if len(analysis['chunks']) > max_chunks:
            console.print(f"[dim]... and {len(analysis['chunks']) - max_chunks} more chunks[/dim]")
            console.print(f"[dim]Use --max-chunks to show more chunks[/dim]")

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def interactive():
    """Start interactive query mode with corrective RAG"""
    rag = get_rag_system()

    if not rag.load_vectorstore():
        console.print("[red]Error: No vector store found. Please add documents first.[/red]")
        raise typer.Exit(1)

    if not rag.openai_api_key:
        console.print("[red]Error: OpenAI API key not found. Please set OPENAI_API_KEY environment variable.[/red]")
        raise typer.Exit(1)

    try:
        console.print("[green]Corrective RAG system ready! Type 'quit' to exit.[/green]")
        console.print("[dim]Features: Self-correction, relevance grading, web search fallback[/dim]\n")

        while True:
            question = typer.prompt("\nEnter your question")

            if question.lower() in ['quit', 'exit', 'q']:
                console.print("[yellow]Goodbye![/yellow]")
                break

            try:
                with console.status("[bold green]Processing with self-correction..."):
                    result = rag.query(question, return_diagnostics=True)

                console.print(Panel(result["answer"], title="Answer", border_style="green"))
                
                # Show quick diagnostics
                if "diagnostics" in result:
                    diag = result["diagnostics"]
                    info_text = f"[dim]Retrieved: {diag['total_retrieved']} | Relevant: {diag['relevant_count']} | "
                    info_text += f"Web Search: {'Yes' if diag['used_web_search'] else 'No'}[/dim]"
                    console.print(info_text)

            except Exception as e:
                console.print(f"[red]Error: {e}[/red]")

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()

"""
Comparison Demo: Traditional RAG vs Corrective RAG
This script demonstrates the difference between the two approaches
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.rag_system import RAGSystem
from src.corrective_rag_system import CorrectiveRAGSystem
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.columns import Columns

console = Console()


def compare_systems():
    """Compare Traditional RAG vs Corrective RAG on the same query"""
    
    console.print("\n[bold magenta]═══════════════════════════════════════════════════════════════[/bold magenta]")
    console.print("[bold magenta]      Traditional RAG vs Corrective RAG - Side by Side      [/bold magenta]")
    console.print("[bold magenta]═══════════════════════════════════════════════════════════════[/bold magenta]\n")
    
    # Check API key
    if not os.getenv("OPENAI_API_KEY"):
        console.print("[red]Error: OPENAI_API_KEY not set[/red]")
        return
    
    # Initialize both systems
    console.print("[cyan]Initializing systems...[/cyan]")
    traditional_rag = RAGSystem()
    corrective_rag = CorrectiveRAGSystem(
        relevance_threshold=0.6,
        use_web_search=True
    )
    
    # Load vector stores
    if not traditional_rag.load_vectorstore():
        console.print("[yellow]No vector store found. Please add documents first:[/yellow]")
        console.print("[yellow]uv run python cli.py add-directory examples/sample_documents[/yellow]")
        return
    
    corrective_rag.load_vectorstore()
    
    # Test query
    question = "What is Python programming?"
    console.print(f"\n[bold]Test Question:[/bold] {question}\n")
    
    # === Traditional RAG ===
    console.print("[bold cyan]Processing with Traditional RAG...[/bold cyan]")
    traditional_rag.setup_qa_chain(retriever_k=4)
    
    with console.status("[green]Querying traditional RAG..."):
        traditional_result = traditional_rag.query(question)
    
    # === Corrective RAG ===
    console.print("[bold cyan]Processing with Corrective RAG...[/bold cyan]")
    
    with console.status("[green]Querying corrective RAG with self-correction..."):
        corrective_result = corrective_rag.query(question, k=4, return_diagnostics=True)
    
    # === Display Results Side by Side ===
    console.print("\n[bold yellow]═══════════════════════════════════════════════════════════════[/bold yellow]")
    console.print("[bold yellow]                         RESULTS COMPARISON                       [/bold yellow]")
    console.print("[bold yellow]═══════════════════════════════════════════════════════════════[/bold yellow]\n")
    
    # Create comparison table
    comparison = Table(title="Answer Quality Comparison", show_header=True)
    comparison.add_column("System", style="cyan", width=20)
    comparison.add_column("Answer", style="white", width=60)
    
    comparison.add_row(
        "Traditional RAG",
        traditional_result["answer"][:200] + "..."
    )
    comparison.add_row(
        "Corrective RAG",
        corrective_result["answer"][:200] + "..."
    )
    
    console.print(comparison)
    
    # === Process Comparison ===
    console.print("\n[bold yellow]Process Details:[/bold yellow]\n")
    
    # Traditional RAG process
    trad_table = Table(title="Traditional RAG Process", border_style="blue")
    trad_table.add_column("Step", style="cyan")
    trad_table.add_column("Action", style="white")
    
    trad_table.add_row("1", "Retrieved 4 documents")
    trad_table.add_row("2", "Used ALL documents (no filtering)")
    trad_table.add_row("3", "Generated answer")
    trad_table.add_row("Quality Check", "❌ None")
    trad_table.add_row("Fallback", "❌ None")
    
    # Corrective RAG process
    corr_table = Table(title="Corrective RAG Process", border_style="green")
    corr_table.add_column("Step", style="cyan")
    corr_table.add_column("Action", style="white")
    
    if "diagnostics" in corrective_result:
        diag = corrective_result["diagnostics"]
        corr_table.add_row("1", f"Retrieved {diag['total_retrieved']} documents")
        corr_table.add_row("2", f"✅ Graded each document for relevance")
        corr_table.add_row("3", f"Kept {diag['relevant_count']} relevant, filtered {diag['irrelevant_count']} irrelevant")
        corr_table.add_row("4", f"{'✅ Used web search' if diag['used_web_search'] else '✗ No web search needed'}")
        corr_table.add_row("5", "Generated answer from corrected context")
        corr_table.add_row("Quality Check", f"✅ {diag['relevance_ratio']:.0%} relevance ratio")
        corr_table.add_row("Fallback", "✅ Web search available")
    
    # Display side by side
    console.print(Columns([trad_table, corr_table]))
    
    # === Detailed Diagnostics ===
    if "diagnostics" in corrective_result:
        console.print("\n[bold magenta]Corrective RAG Diagnostics:[/bold magenta]\n")
        
        diag = corrective_result["diagnostics"]
        
        # Grading results
        console.print("[bold]Document Grading:[/bold]")
        for i, grade in enumerate(diag["grading_results"], 1):
            icon = "✓" if grade["is_relevant"] else "✗"
            color = "green" if grade["is_relevant"] else "red"
            console.print(f"  [{color}]{icon}[/{color}] Doc {i}: {grade['content_preview']}")
        
        # Metrics
        console.print("\n[bold]Metrics:[/bold]")
        metrics_table = Table(show_header=False, box=None)
        metrics_table.add_column("Metric", style="cyan")
        metrics_table.add_column("Value", style="yellow")
        
        metrics_table.add_row("Relevance Ratio", f"{diag['relevance_ratio']:.1%}")
        metrics_table.add_row("Web Search Used", "Yes ✓" if diag["used_web_search"] else "No ✗")
        metrics_table.add_row("Quality Filtered", f"{diag['irrelevant_count']} docs removed")
        
        console.print(metrics_table)
    
    # === Summary ===
    console.print("\n[bold yellow]═══════════════════════════════════════════════════════════════[/bold yellow]")
    console.print("[bold yellow]                            SUMMARY                              [/bold yellow]")
    console.print("[bold yellow]═══════════════════════════════════════════════════════════════[/bold yellow]\n")
    
    summary_table = Table(show_header=True)
    summary_table.add_column("Feature", style="cyan", width=30)
    summary_table.add_column("Traditional RAG", style="blue", width=20)
    summary_table.add_column("Corrective RAG", style="green", width=20)
    
    summary_table.add_row("Document Filtering", "❌ None", "✅ Yes")
    summary_table.add_row("Relevance Check", "❌ None", "✅ LLM-based")
    summary_table.add_row("Web Search Fallback", "❌ None", "✅ Yes")
    summary_table.add_row("Quality Control", "❌ None", "✅ Automatic")
    summary_table.add_row("Diagnostics", "❌ Limited", "✅ Detailed")
    summary_table.add_row("Self-Correction", "❌ No", "✅ Yes")
    
    if "diagnostics" in corrective_result:
        diag = corrective_result["diagnostics"]
        summary_table.add_row(
            "Documents Used",
            f"{len(traditional_result['source_documents'])} (all)",
            f"{diag['relevant_count']} (filtered)"
        )
    
    console.print(summary_table)
    
    # === Recommendations ===
    console.print("\n[bold cyan]When to Use:[/bold cyan]\n")
    
    console.print("[bold blue]Traditional RAG:[/bold blue]")
    console.print("  • When all documents are high quality")
    console.print("  • When speed is critical")
    console.print("  • When cost needs to be minimized")
    
    console.print("\n[bold green]Corrective RAG:[/bold green]")
    console.print("  • When document quality varies")
    console.print("  • When accuracy is paramount")
    console.print("  • When you need transparency")
    console.print("  • When fallback to web is useful")
    
    console.print("\n[bold magenta]═══════════════════════════════════════════════════════════════[/bold magenta]")
    console.print("[bold green]✅ Corrective RAG provides better quality control and transparency![/bold green]")
    console.print("[bold magenta]═══════════════════════════════════════════════════════════════[/bold magenta]\n")


if __name__ == "__main__":
    try:
        compare_systems()
    except KeyboardInterrupt:
        console.print("\n[yellow]Comparison interrupted[/yellow]")
    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]")
        import traceback
        console.print(f"[dim]{traceback.format_exc()}[/dim]")


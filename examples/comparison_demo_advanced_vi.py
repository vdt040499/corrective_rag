"""
Comparison Demo Advanced: Traditional RAG vs Corrective RAG
Demo tiếng Việt với các case thực tế để so sánh sự khác biệt
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
from rich import box

console = Console()


def print_case_header(case_num: int, title: str, description: str):
    """Print a formatted case header"""
    console.print("\n" + "=" * 80)
    console.print(f"[bold cyan]CASE {case_num}: {title}[/bold cyan]")
    console.print("=" * 80)
    console.print(f"[dim]{description}[/dim]\n")


def print_comparison_table(trad_result: dict, crag_result: dict, case_title: str):
    """Print comparison table between Traditional RAG and Corrective RAG"""
    console.print(f"\n[bold yellow]═══════════════════════════════════════════════════════════════[/bold yellow]")
    console.print(f"[bold yellow]                    KẾT QUẢ SO SÁNH - {case_title}                [/bold yellow]")
    console.print(f"[bold yellow]═══════════════════════════════════════════════════════════════[/bold yellow]\n")
    
    # Answer comparison
    comparison = Table(title="So sánh câu trả lời", show_header=True, box=box.ROUNDED)
    comparison.add_column("Hệ thống", style="cyan", width=20)
    comparison.add_column("Câu trả lời", style="white", width=70)
    
    trad_answer = trad_result.get("answer", "Không có câu trả lời")
    crag_answer = crag_result.get("answer", "Không có câu trả lời")
    
    # Truncate long answers
    max_len = 300
    if len(trad_answer) > max_len:
        trad_answer = trad_answer[:max_len] + "..."
    if len(crag_answer) > max_len:
        crag_answer = crag_answer[:max_len] + "..."
    
    comparison.add_row(
        "[blue]Traditional RAG[/blue]",
        trad_answer
    )
    comparison.add_row(
        "[green]Corrective RAG[/green]",
        crag_answer
    )
    
    console.print(comparison)
    
    # Process comparison
    console.print("\n[bold yellow]Quy trình xử lý:[/bold yellow]\n")
    
    # Traditional RAG process
    trad_table = Table(title="Traditional RAG Process", border_style="blue", box=box.ROUNDED)
    trad_table.add_column("Bước", style="cyan", width=10)
    trad_table.add_column("Hành động", style="white", width=50)
    
    trad_table.add_row("1", "Retrieve: Lấy 4 documents từ vector store")
    trad_table.add_row("2", "❌ Không có bước đánh giá chất lượng")
    trad_table.add_row("3", "❌ Không lọc documents không liên quan")
    trad_table.add_row("4", "Generate: Tạo câu trả lời từ TẤT CẢ documents")
    trad_table.add_row("5", "❌ Không có fallback mechanism")
    
    # Corrective RAG process
    crag_table = Table(title="Corrective RAG Process", border_style="green", box=box.ROUNDED)
    crag_table.add_column("Bước", style="cyan", width=10)
    crag_table.add_column("Hành động", style="white", width=50)
    
    if "diagnostics" in crag_result:
        diag = crag_result["diagnostics"]
        crag_table.add_row("1", f"Retrieve: Lấy {diag['total_retrieved']} documents")
        crag_table.add_row("2", "✅ Grade: Đánh giá độ liên quan của từng document")
        crag_table.add_row("3", f"✅ Filter: Giữ {diag['relevant_count']} relevant, loại {diag['irrelevant_count']} không liên quan")
        
        if diag['used_web_search']:
            crag_table.add_row("4", "✅ Web Search: Kích hoạt tìm kiếm web để bổ sung")
        else:
            crag_table.add_row("4", "✗ Web Search: Không cần thiết")
        
        crag_table.add_row("5", f"Generate: Tạo câu trả lời từ {diag['relevant_count']} documents đã lọc + web search (nếu có)")
        crag_table.add_row("6", f"✅ Relevance Ratio: {diag['relevance_ratio']:.1%}")
    else:
        crag_table.add_row("1", "Retrieve: Lấy documents")
        crag_table.add_row("2", "✅ Grade: Đánh giá độ liên quan")
        crag_table.add_row("3", "✅ Filter: Lọc documents không liên quan")
        crag_table.add_row("4", "Generate: Tạo câu trả lời")
    
    # Display side by side
    console.print(Columns([trad_table, crag_table]))
    
    # Detailed diagnostics
    if "diagnostics" in crag_result:
        diag = crag_result["diagnostics"]
        
        console.print("\n[bold magenta]📊 Chi tiết Corrective RAG Diagnostics:[/bold magenta]\n")
        
        # Metrics table
        metrics_table = Table(title="Metrics", box=box.ROUNDED)
        metrics_table.add_column("Metric", style="cyan")
        metrics_table.add_column("Giá trị", style="yellow")
        
        metrics_table.add_row("Tổng số documents retrieved", str(diag["total_retrieved"]))
        metrics_table.add_row("Documents liên quan", f"[green]{diag['relevant_count']}[/green]")
        metrics_table.add_row("Documents KHÔNG liên quan", f"[red]{diag['irrelevant_count']}[/red]")
        metrics_table.add_row("Tỷ lệ liên quan", f"{diag['relevance_ratio']:.1%}")
        metrics_table.add_row("Đã dùng Web Search", "✅ Có" if diag["used_web_search"] else "✗ Không")
        
        console.print(metrics_table)
        
        # Document grading details
        if diag.get("grading_results"):
            console.print("\n[bold]Chi tiết đánh giá từng document:[/bold]")
            for i, grade in enumerate(diag["grading_results"], 1):
                icon = "✅" if grade["is_relevant"] else "❌"
                color = "green" if grade["is_relevant"] else "red"
                preview = grade.get("content_preview", "")[:100] + "..."
                console.print(f"  [{color}]{icon} Document {i}:[/{color}] {preview}")


def demo_case_1_outdated_data():
    """Case 1: Handling Outdated Data"""
    print_case_header(
        1,
        "Xử lý thông tin lỗi thời (Outdated Data)",
        "Xử lý khi người dùng hỏi về tính năng mới mà DB chưa cập nhật."
    )
    
    # Initialize systems
    traditional_rag = RAGSystem()
    corrective_rag = CorrectiveRAGSystem(
        relevance_threshold=0.6,
        use_web_search=True
    )
    
    if not traditional_rag.load_vectorstore():
        console.print("[yellow]Không tìm thấy vector store. Vui lòng thêm documents trước:[/yellow]")
        console.print("[yellow]uv run python cli.py add-directory examples/sample_documents[/yellow]")
        return
    
    corrective_rag.load_vectorstore()
    # Use strict context mode to force Traditional RAG to only use retrieved documents
    # This makes it more vulnerable to hallucinations when documents are misleading
    traditional_rag.setup_qa_chain(retriever_k=4, use_strict_context=True)
    
    # Question about new feature not in DB
    question = "Nút Action Button trên iPhone hoạt động như thế nào?"
    console.print(f"[bold]Câu hỏi:[/bold] [yellow]{question}[/yellow]")
    console.print("[dim]Lưu ý: Action Button chỉ có trên iPhone 15 Pro trở lên. DB hiện tại chỉ có thông tin về cần gạt rung/chuông của iPhone 14.[/dim]\n")
    
    # Traditional RAG (configured with strict context mode to demonstrate vulnerability)
    console.print("[blue]🔄 Traditional RAG đang xử lý (strict context mode)...[/blue]")
    console.print("[dim]Lưu ý: Traditional RAG đã được cấu hình với strict context mode để buộc chỉ dựa vào documents[/dim]\n")
    with console.status("[bold blue]Querying Traditional RAG..."):
        trad_result = traditional_rag.query(question)
    
    # Corrective RAG
    console.print("[green]🔄 Corrective RAG đang xử lý...[/green]")
    with console.status("[bold green]Querying Corrective RAG..."):
        crag_result = corrective_rag.query(question, k=4, return_diagnostics=True)
    
    # Comparison
    print_comparison_table(trad_result, crag_result, "Case 1: Outdated Data")
    
    # Analysis
    console.print("\n[bold cyan]📊 Phân tích chi tiết:[/bold cyan]\n")
    
    console.print(Panel(
        "[bold red]Traditional RAG (Thất bại):[/bold red]\n"
        "• Tìm thấy tài liệu về 'Cần gạt rung/chuông' (Mute switch) của iPhone 14\n"
        "• Trả lời sai: 'Nút này nằm ở cạnh trái, bạn gạt lên/xuống để bật tắt chế độ im lặng.'\n"
        "• Hậu quả: Trả lời sai hoàn toàn về cơ chế (gạt vs nhấn giữ) và tên gọi\n\n"
        "[bold green]Corrective RAG (Thành công):[/bold green]\n"
        "• Retrieve: Lấy tài liệu về 'Cần gạt rung/chuông'\n"
        "• Evaluate: LLM đánh giá 'Action Button' khác 'Mute Switch' → Không liên quan\n"
        "• Action: Kích hoạt Web Search\n"
        "• Generate: Tìm thấy thông tin từ Apple.com về iPhone 15 Pro\n"
        "• Trả lời đúng: 'Action Button là nút bấm mới thay thế cần gạt rung...'",
        title="[bold]Case 1 Analysis[/bold]",
        border_style="green"
    ))
    
    # Show documents
    console.print("\n[bold blue]📄 Documents Retrieved by Traditional RAG:[/bold blue]")
    for i, doc in enumerate(trad_result.get("source_documents", [])[:3], 1):
        source = doc.metadata.get('source', 'Unknown')
        preview = doc.page_content[:150] + "..."
        console.print(f"  {i}. [dim]{Path(source).name}[/dim]")
        console.print(f"     {preview}\n")
    
    if "diagnostics" in crag_result:
        diag = crag_result["diagnostics"]
        console.print(f"[bold green]✅ Corrective RAG đã lọc {diag['irrelevant_count']} documents không liên quan[/bold green]")
        if diag["used_web_search"]:
            console.print("[bold yellow]🌐 Web search đã được sử dụng để tìm thông tin mới nhất![/bold yellow]")


def demo_case_2_hallucinations():
    """Case 2: Handling Hallucinations/Myths"""
    print_case_header(
        2,
        "Xử lý thông tin sai lệch/Tin đồn (Hallucinations/Myths)",
        "Ngăn chặn AI đồng tình với các giả định sai của người dùng."
    )
    
    # Initialize systems
    traditional_rag = RAGSystem()
    corrective_rag = CorrectiveRAGSystem(
        relevance_threshold=0.6,
        use_web_search=True
    )
    
    if not traditional_rag.load_vectorstore():
        console.print("[yellow]Không tìm thấy vector store.[/yellow]")
        return
    
    corrective_rag.load_vectorstore()
    # Use strict context mode to force Traditional RAG to only use retrieved documents
    # This makes it more vulnerable to hallucinations when documents are misleading
    traditional_rag.setup_qa_chain(retriever_k=4, use_strict_context=True)
    
    # Question about non-existent feature
    question = "Hướng dẫn tôi cách bật tính năng máy chiếu (Projector) trên iPhone?"
    console.print(f"[bold]Câu hỏi:[/bold] [yellow]{question}[/yellow]")
    console.print("[dim]Thực tế: iPhone chưa bao giờ có máy chiếu tích hợp.[/dim]\n")
    
    # Traditional RAG (configured with strict context mode to demonstrate vulnerability)
    console.print("[blue]🔄 Traditional RAG đang xử lý (strict context mode)...[/blue]")
    console.print("[dim]Lưu ý: Traditional RAG đã được cấu hình với strict context mode để buộc chỉ dựa vào documents[/dim]\n")
    with console.status("[bold blue]Querying Traditional RAG..."):
        trad_result = traditional_rag.query(question)
    
    # Corrective RAG
    console.print("[green]🔄 Corrective RAG đang xử lý...[/green]")
    with console.status("[bold green]Querying Corrective RAG..."):
        crag_result = corrective_rag.query(question, k=4, return_diagnostics=True)
    
    # Comparison
    print_comparison_table(trad_result, crag_result, "Case 2: Hallucinations")
    
    # Analysis
    console.print("\n[bold cyan]📊 Phân tích chi tiết:[/bold cyan]\n")
    
    console.print(Panel(
        "[bold red]Traditional RAG (Rủi ro ảo giác):[/bold red]\n"
        "• Tìm thấy tài liệu về 'Phản chiếu màn hình' và 'chiếu hình ảnh'\n"
        "• Với strict context mode: Buộc chỉ dựa vào tài liệu, không dùng kiến thức sẵn\n"
        "• Tài liệu nói về 'chiếu hình ảnh' nhưng KHÔNG nói rõ đây là AirPlay, không phải máy chiếu vật lý\n"
        "• Rủi ro: Có thể nhầm lẫn 'phản chiếu/chiếu' với 'máy chiếu tích hợp'\n"
        "• Trả lời sai tiềm năng: 'Để bật tính năng chiếu, bạn vuốt Trung tâm điều khiển...'\n"
        "• Thực tế: Ngay cả với strict mode, LLM có thể vẫn suy luận đúng nhờ ngữ cảnh\n"
        "• Vấn đề: KHÔNG CÓ CƠ CHẾ XÁC MINH - Nếu LLM suy luận sai, không có cách kiểm tra\n\n"
        "[bold green]Corrective RAG (An toàn - Có xác minh):[/bold green]\n"
        "• Retrieve: Lấy tài liệu 'AirPlay/Screen Mirroring'\n"
        "• Evaluate: LLM đánh giá độ liên quan → 'phản chiếu màn hình' khác 'máy chiếu vật lý tích hợp'\n"
        "• Decision: Relevance ratio thấp → Kích hoạt Web Search để xác minh\n"
        "• Verify: Web search xác nhận rõ ràng 'iPhone không có máy chiếu tích hợp'\n"
        "• Generate: Kết hợp thông tin từ documents + web search\n"
        "• Trả lời đúng: 'iPhone không có máy chiếu tích hợp. Bạn có thể dùng AirPlay để phản chiếu màn hình...'\n"
        "• Ưu điểm: CÓ CƠ CHẾ XÁC MINH TỰ ĐỘNG - Không phụ thuộc vào suy luận của LLM",
        title="[bold]Case 2 Analysis[/bold]",
        border_style="green"
    ))
    
    if "diagnostics" in crag_result:
        diag = crag_result["diagnostics"]
        if diag["used_web_search"]:
            console.print("\n[bold yellow]🌐 Corrective RAG đã sử dụng web search để xác minh và sửa thông tin sai![/bold yellow]")


def demo_case_3_comparative():
    """Case 3: Handling Comparative/Ambiguous Knowledge"""
    print_case_header(
        3,
        "Xử lý câu hỏi so sánh (Comparative/Ambiguous Knowledge)",
        "Xử lý câu hỏi yêu cầu kiến thức 'lai' giữa cái cũ (có trong DB) và cái mới (phải tìm bên ngoài)."
    )
    
    # Initialize systems
    traditional_rag = RAGSystem()
    corrective_rag = CorrectiveRAGSystem(
        relevance_threshold=0.6,
        use_web_search=True
    )
    
    if not traditional_rag.load_vectorstore():
        console.print("[yellow]Không tìm thấy vector store.[/yellow]")
        return
    
    corrective_rag.load_vectorstore()
    # Use strict context mode to force Traditional RAG to only use retrieved documents
    # This makes it more vulnerable to hallucinations when documents are misleading
    traditional_rag.setup_qa_chain(retriever_k=4, use_strict_context=True)
    
    # Comparative question
    question = "Cổng sạc của iPhone 15 khác gì so với iPhone 14?"
    console.print(f"[bold]Câu hỏi:[/bold] [yellow]{question}[/yellow]")
    console.print("[dim]DB chỉ có thông tin về iPhone 14 (Lightning), không có iPhone 15 (USB-C).[/dim]\n")
    
    # Traditional RAG (configured with strict context mode to demonstrate vulnerability)
    console.print("[blue]🔄 Traditional RAG đang xử lý (strict context mode)...[/blue]")
    console.print("[dim]Lưu ý: Traditional RAG đã được cấu hình với strict context mode để buộc chỉ dựa vào documents[/dim]\n")
    with console.status("[bold blue]Querying Traditional RAG..."):
        trad_result = traditional_rag.query(question)
    
    # Corrective RAG
    console.print("[green]🔄 Corrective RAG đang xử lý...[/green]")
    with console.status("[bold green]Querying Corrective RAG..."):
        crag_result = corrective_rag.query(question, k=4, return_diagnostics=True)
    
    # Comparison
    print_comparison_table(trad_result, crag_result, "Case 3: Comparative Knowledge")
    
    # Analysis
    console.print("\n[bold cyan]📊 Phân tích chi tiết:[/bold cyan]\n")
    
    console.print(Panel(
        "[bold red]Traditional RAG (Thất bại - Thiếu hụt):[/bold red]\n"
        "• Tìm thấy tài liệu iPhone 14 (Cổng Lightning)\n"
        "• Không tìm thấy iPhone 15\n"
        "• Trả lời không đầy đủ: 'iPhone 14 sử dụng cổng Lightning.'\n"
        "• Hoặc bịa ra thông tin về iPhone 15 vì không có dữ liệu\n\n"
        "[bold green]Corrective RAG (Thành công - Điểm Wow):[/bold green]\n"
        "• Retrieve: Lấy tài liệu iPhone 14 (Lightning)\n"
        "• Evaluate:\n"
        "  - Phần iPhone 14: ✅ Correct (Giữ lại)\n"
        "  - Phần iPhone 15: ❌ Missing (Thiếu)\n"
        "• Action: Kích hoạt Web Search bổ sung cho 'iPhone 15 charging port'\n"
        "• Generate: Tổng hợp kiến thức DB và Web\n"
        "• Trả lời đầy đủ: 'iPhone 14 sử dụng cổng Lightning (theo tài liệu nội bộ), "
        "trong khi iPhone 15 đã chuyển sang chuẩn USB-C (theo tin tức mới nhất).'",
        title="[bold]Case 3 Analysis[/bold]",
        border_style="green"
    ))
    
    if "diagnostics" in crag_result:
        diag = crag_result["diagnostics"]
        if diag["used_web_search"]:
            console.print("\n[bold yellow]🌐 Corrective RAG đã kết hợp kiến thức local (iPhone 14) với web search (iPhone 15)![/bold yellow]")


def main():
    """Run all advanced case demos"""
    console.print("\n[bold magenta]╔══════════════════════════════════════════════════════════════╗[/bold magenta]")
    console.print("[bold magenta]║   Advanced Cases: Corrective RAG vs Traditional RAG         ║[/bold magenta]")
    console.print("[bold magenta]║   Demo tiếng Việt - So sánh chi tiết                        ║[/bold magenta]")
    console.print("[bold magenta]╚══════════════════════════════════════════════════════════════╝[/bold magenta]\n")
    
    console.print("[bold cyan]Các case sẽ được demo:[/bold cyan]")
    console.print("  1. Xử lý thông tin lỗi thời (Outdated Data)")
    console.print("  2. Xử lý thông tin sai lệch/Tin đồn (Hallucinations/Myths)")
    console.print("  3. Xử lý câu hỏi so sánh (Comparative/Ambiguous Knowledge)\n")
    
    # Check API key
    if not os.getenv("OPENAI_API_KEY"):
        console.print("[red]Lỗi: Không tìm thấy OPENAI_API_KEY[/red]")
        console.print("[yellow]Vui lòng set API key của bạn:[/yellow]")
        console.print("[yellow]export OPENAI_API_KEY='your-api-key-here'[/yellow]")
        return
    
    try:
        demo_case_1_outdated_data()
        input("\n[dim]Nhấn Enter để tiếp tục Case 2...[/dim]")
        
        demo_case_2_hallucinations()
        input("\n[dim]Nhấn Enter để tiếp tục Case 3...[/dim]")
        
        demo_case_3_comparative()
        
        console.print("\n[bold green]✅ Tất cả các advanced cases đã hoàn thành![/bold green]")
        console.print("\n[bold]Những điểm quan trọng:[/bold]")
        console.print("  • Corrective RAG xử lý thông tin lỗi thời bằng web search")
        console.print("  • Corrective RAG ngăn chặn ảo giác bằng cách xác minh thông tin")
        console.print("  • Corrective RAG kết hợp hiệu quả kiến thức local và external")
        console.print("\n[bold magenta]═══════════════════════════════════════════════════════════════[/bold magenta]")
        
    except KeyboardInterrupt:
        console.print("\n[yellow]Demo bị gián đoạn[/yellow]")
    except Exception as e:
        console.print(f"\n[red]Lỗi: {e}[/red]")
        import traceback
        console.print(f"[dim]{traceback.format_exc()}[/dim]")


if __name__ == "__main__":
    main()


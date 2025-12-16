# Corrective RAG Project

Hệ thống **Corrective Retrieval-Augmented Generation (CRAG)** với cơ chế tự sửa lỗi, đánh giá độ liên quan và web search fallback.

## 🎯 Tính năng chính

- **🔍 Đánh giá độ liên quan**: Tự động đánh giá documents có liên quan đến câu hỏi không
- **✅ Tự sửa lỗi**: Lọc bỏ documents không liên quan trước khi tạo câu trả lời
- **🌐 Web Search Fallback**: Tự động tìm kiếm web khi documents local không đủ
- **📊 Diagnostics**: Hiển thị chi tiết quá trình xử lý và đánh giá

## 🚀 Cài đặt

```bash
# Cài đặt dependencies
uv sync

# Set OpenAI API key
export OPENAI_API_KEY='your-api-key-here'
```

## 📖 Quick Start

### 1. Thêm documents

```bash
uv run python cli.py add-directory examples/sample_documents
```

### 2. Chạy Web Demo

```bash
uv run streamlit run demo.py
```

Demo sẽ hiển thị 3 cases so sánh Traditional RAG vs Corrective RAG với diagnostics chi tiết.

### 3. Sử dụng CLI

```bash
# Query đơn giản
uv run python cli.py query "Câu hỏi của bạn"

# Query với diagnostics
uv run python cli.py query "Câu hỏi của bạn" --diagnostics

# Interactive mode
uv run python cli.py interactive
```

### 4. REST API

```bash
# Khởi động server
uv run python main.py

# API sẽ chạy tại http://localhost:8000
# Xem docs tại http://localhost:8000/docs
```

## 📁 Cấu trúc Project

```
rag-project/
├── src/
│   ├── rag_system.py              # Traditional RAG
│   ├── corrective_rag_system.py    # Corrective RAG
│   └── api.py                     # FastAPI REST API
├── examples/
│   └── sample_documents/          # Sample documents
├── demo.py                        # Streamlit web demo
├── cli.py                         # CLI interface
└── main.py                        # FastAPI server
```

## 🔧 Cấu hình

Các tham số có thể điều chỉnh trong `CorrectiveRAGSystem`:

- `relevance_threshold`: Ngưỡng độ liên quan (mặc định: 0.7)
- `use_web_search`: Bật/tắt web search fallback (mặc định: True)
- `retriever_k`: Số lượng documents retrieve (mặc định: 4)

## 📚 Tài liệu

- [CORRECTIVE_RAG.md](CORRECTIVE_RAG.md) - Giải thích chi tiết về Corrective RAG
- [OPENAI_EMBEDDINGS.md](OPENAI_EMBEDDINGS.md) - Thông tin về OpenAI embeddings
- [QUICKSTART.md](QUICKSTART.md) - Hướng dẫn nhanh

## 🎓 3 Cases Demo

Demo web (`demo.py`) bao gồm 3 cases:

1. **Outdated Data**: Tính năng mới không có trong DB (Action Button)
2. **Hallucinations**: Tính năng không tồn tại (Máy chiếu tích hợp)
3. **Comparative**: Câu hỏi so sánh giữa cũ và mới (iPhone 14 vs 15)

Mỗi case hiển thị:
- Câu trả lời của Traditional RAG vs Corrective RAG
- Diagnostics chi tiết (documents retrieved, relevance ratio, web search status)
- Chi tiết đánh giá từng document

## 📝 License

MIT License

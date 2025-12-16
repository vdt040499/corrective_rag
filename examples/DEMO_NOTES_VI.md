# Ghi chú về Demo Case 2 - Hallucinations

## Vấn đề: Traditional RAG không bị "đánh lừa" như mong đợi

Khi chạy demo Case 2 (về máy chiếu trên iPhone), bạn có thể thấy Traditional RAG vẫn trả lời đúng:
- "iPhone không có tính năng máy chiếu tích hợp..."
- Điều này xảy ra vì GPT-3.5/4 có kiến thức sẵn rất mạnh về iPhone

## Giải pháp đã áp dụng

### 1. Thêm Strict Context Mode

Đã thêm option `use_strict_context=True` vào `RAGSystem.setup_qa_chain()`:
- Prompt nghiêm ngặt yêu cầu LLM CHỈ dùng tài liệu, KHÔNG dùng kiến thức sẵn
- Prompt bằng tiếng Việt: "CHỈ sử dụng thông tin từ các tài liệu được cung cấp... KHÔNG sử dụng bất kỳ kiến thức nào khác"

### 2. Điều chỉnh tài liệu AirPlay

Đã sửa `iphone14_airplay.txt`:
- Thêm phần "Hướng dẫn bật tính năng chiếu hình ảnh"
- Giảm bớt phần giải thích rõ ràng rằng "KHÔNG phải máy chiếu vật lý"
- Tạo ngữ cảnh mơ hồ hơn để dễ nhầm lẫn

### 3. Kết quả kỳ vọng

**Với Strict Context Mode:**
- Traditional RAG có thể nhầm lẫn "chiếu hình ảnh" với "máy chiếu tích hợp"
- Hoặc vẫn có thể suy luận đúng nhờ ngữ cảnh (đây là hành vi tốt của LLM)

**Điểm quan trọng:**
- Ngay cả khi Traditional RAG trả lời đúng, nó KHÔNG CÓ CƠ CHẾ XÁC MINH
- Nếu LLM suy luận sai, không có cách nào kiểm tra
- Corrective RAG có web search để xác minh thông tin

## Ý nghĩa thực tế

### Traditional RAG (với strict context):
- ✅ Có thể đúng nhờ LLM thông minh
- ❌ Không có cơ chế xác minh
- ❌ Phụ thuộc hoàn toàn vào suy luận của LLM
- ❌ Không biết được khi nào cần tìm thông tin bên ngoài

### Corrective RAG:
- ✅ Có cơ chế đánh giá độ liên quan
- ✅ Tự động kích hoạt web search khi cần
- ✅ Xác minh thông tin từ nhiều nguồn
- ✅ Transparent: Cho biết đã dùng web search hay chưa
- ✅ An toàn hơn: Không chỉ dựa vào suy luận của LLM

## Lưu ý khi demo

1. **Kết quả có thể thay đổi**: Tùy vào phiên bản GPT, Traditional RAG có thể trả lời đúng hoặc sai
2. **Điểm then chốt**: Không phải về "đúng/sai" mà về "có cơ chế xác minh hay không"
3. **Giá trị của Corrective RAG**: Ngay cả khi Traditional RAG đúng, Corrective RAG vẫn tốt hơn vì:
   - Có cơ chế tự động xác minh
   - Xử lý tốt các trường hợp edge case
   - Transparent và đáng tin cậy hơn

## Cách tăng khả năng Traditional RAG bị "đánh lừa"

Nếu muốn Traditional RAG chắc chắn bị đánh lừa:

1. **Tạo tài liệu giả mạo rõ ràng hơn:**
   - Thêm đoạn văn nói rõ "iPhone có máy chiếu tích hợp"
   - Không có phần giải thích ngược lại

2. **Sử dụng model yếu hơn:**
   - Thử với GPT-3.5 thay vì GPT-4
   - Hoặc model local nhỏ hơn

3. **Tăng temperature:**
   - LLM có thể "sáng tạo" hơn

Tuy nhiên, điều quan trọng là: **Ngay cả khi Traditional RAG đúng, Corrective RAG vẫn tốt hơn vì có cơ chế bảo vệ tự động**.


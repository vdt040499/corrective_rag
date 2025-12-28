"""
Streamlit Demo: Corrective RAG vs Traditional RAG
Demo web interface để so sánh 3 cases giữa Traditional RAG và Corrective RAG
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import streamlit as st
from src.rag_system import RAGSystem
from src.corrective_rag_system import CorrectiveRAGSystem

# Page config
st.set_page_config(
    page_title="Corrective RAG Demo",
    page_icon="🔍",
    layout="wide"
)

# Initialize session state
if "systems_initialized" not in st.session_state:
    st.session_state.systems_initialized = False
    st.session_state.traditional_rag = None
    st.session_state.corrective_rag = None
    st.session_state.case_results = {}  # Cache for case results

def initialize_systems():
    """Initialize RAG systems"""
    if not st.session_state.systems_initialized:
        with st.spinner("Initializing systems..."):
            try:
                st.session_state.traditional_rag = RAGSystem()
                st.session_state.corrective_rag = CorrectiveRAGSystem(
                    min_relevant_docs=1,  # Dynamic threshold: require at least 1 relevant doc
                    use_web_search=True
                )
                
                if not st.session_state.traditional_rag.load_vectorstore():
                    st.error("❌ Vector store not found. Please add documents first:")
                    st.code("uv run python cli.py add-directory examples/sample_documents")
                    return False
                
                st.session_state.corrective_rag.load_vectorstore()
                st.session_state.traditional_rag.setup_qa_chain(retriever_k=4, use_strict_context=True)
                st.session_state.systems_initialized = True
                return True
            except Exception as e:
                st.error(f"Initialization error: {e}")
                return False
    return True

def display_diagnostics(crag_result):
    """Display detailed diagnostics for Corrective RAG"""
    if "diagnostics" not in crag_result:
        return
    
    diag = crag_result["diagnostics"]
    
    st.subheader("📊 Corrective RAG Diagnostics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Documents Retrieved", diag["total_retrieved"])
    
    with col2:
        st.metric("✅ Relevant", diag["relevant_count"], delta=None)
    
    with col3:
        st.metric("❌ Irrelevant", diag["irrelevant_count"], delta=None)
    
    with col4:
        relevance_ratio = diag["relevance_ratio"]
        st.metric("Relevance Ratio", f"{relevance_ratio:.1%}")
    
    # Threshold information
    if "threshold_used" in diag:
        threshold_type = diag.get("threshold_type", "fixed")
        threshold_value = diag["threshold_used"]
        threshold_label = "🔧 Dynamic Threshold" if threshold_type == "dynamic" else "📌 Fixed Threshold"
        min_relevant = diag.get("min_relevant_docs")
        
        threshold_info = f"{threshold_label}: {threshold_value:.1%}"
        if threshold_type == "dynamic" and min_relevant is not None:
            threshold_info += f" (min {min_relevant} relevant doc{'s' if min_relevant > 1 else ''})"
        st.caption(threshold_info)
    
    # Web search status
    if diag["used_web_search"]:
        st.success("🌐 Web Search activated to supplement information")
    else:
        st.info("ℹ️ Web Search not needed (documents are sufficiently relevant)")
    
    # Document grading details
    if diag.get("grading_results"):
        with st.expander("📋 Document Grading Details"):
            for i, grade in enumerate(diag["grading_results"], 1):
                icon = "✅" if grade["is_relevant"] else "❌"
                status = "Relevant" if grade["is_relevant"] else "Not Relevant"
                color = "green" if grade["is_relevant"] else "red"
                
                st.markdown(f"**Document {i}:** {icon} {status}")
                preview = grade.get("content_preview", "")[:200]
                st.text(preview + "...")
                st.divider()

def run_case(case_num, title, description, question, context_note, use_web_search=True, k=4):
    """Run a demo case with user input"""
    st.markdown("---")
    st.header(f"TH {case_num}: {title}")
    if description:
        st.caption(description)
    
    # Show suggested question as placeholder
    st.markdown("**Nhập câu hỏi của bạn:**")
    user_question = st.text_input(
        f"Question for Case {case_num}:",
        value="",
        # placeholder=question,
        key=f"case_{case_num}_input",
        label_visibility="collapsed"
    )
    
    # Run button
    run_button = st.button(f"Run", type="primary", key=f"case_{case_num}_button", use_container_width=True)
    
    # Only run if button is clicked and question is provided
    if run_button:
        if not user_question.strip():
            st.warning("⚠️ Vui lòng nhập câu hỏi!")
            return
        
        # Run queries
        with st.spinner("Đang xử lý câu hỏi..."):
            # Set retriever_k for Traditional RAG
            st.session_state.traditional_rag.setup_qa_chain(retriever_k=k, use_strict_context=True)
            trad_result = st.session_state.traditional_rag.query(user_question)
            
            # Use separate Corrective RAG instance if web search setting differs
            if use_web_search:
                crag_result = st.session_state.corrective_rag.query(user_question, k=k, return_diagnostics=True)
            else:
                # Create temporary Corrective RAG instance with web search disabled
                temp_crag = CorrectiveRAGSystem(
                    min_relevant_docs=1,  # Dynamic threshold: require at least 1 relevant doc
                    use_web_search=False
                )
                temp_crag.load_vectorstore()
                crag_result = temp_crag.query(user_question, k=k, return_diagnostics=True)
        
        # Display results
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🔵 Traditional RAG")
            st.markdown("**Answer:**")
            st.write(trad_result.get("answer", "Không có câu trả lời"))
            
            # Show source documents
            with st.expander("📄 Source Documents"):
                for i, doc in enumerate(trad_result.get("source_documents", [])[:3], 1):
                    source = doc.metadata.get('source', 'Unknown')
                    st.markdown(f"**Document {i}:** `{Path(source).name}`")
                    st.text(doc.page_content[:200] + "...")
        
        with col2:
            st.subheader("🟢 Corrective RAG")
            st.markdown("**Answer:**")
            st.write(crag_result.get("answer", "Không có câu trả lời"))
            
            # Display diagnostics
            display_diagnostics(crag_result)
            
            # Show relevant documents
            with st.expander("📄 Relevant Documents"):
                relevant_docs = crag_result.get("source_documents", [])
                if relevant_docs:
                    for i, doc in enumerate(relevant_docs[:3], 1):
                        source = doc.metadata.get('source', 'Unknown')
                        st.markdown(f"**Document {i}:** `{Path(source).name}`")
                        st.text(doc.page_content[:200] + "...")
                else:
                    st.info("No relevant documents retained")

def main():
    st.title("Corrective RAG Demo")
    
    # Check API key
    if not os.getenv("OPENAI_API_KEY"):
        st.error("❌ OPENAI_API_KEY not found")
        st.info("Please set API key: `export OPENAI_API_KEY='your-api-key-here'`")
        return
    
    # Initialize systems
    if not initialize_systems():
        return
    
    # Case 0: Documents Relevant
    run_case(
        case_num=1,
        title="Các tài liệu truy xuất liên quan",
        description="Tất cả các tài liệu truy xuất đều liên quan đến câu hỏi",
        question="iPhone 14 có những tính năng và cổng kết nối gì?",
        context_note="💡 This question covers multiple topics in the database (mute switch, Lightning port, AirPlay). All retrieved documents should be relevant. Web search is disabled.",
        use_web_search=False
    )
    
    # Case 1: Outdated Data
    run_case(
        case_num=2,
        title="Thông tin lỗi thời",
        description="Xử lý khi người dùng hỏi về tính năng mới mà DB chưa cập nhật",
        question="Nút Action Button trên iPhone hoạt động như thế nào?",
        context_note="💡 Action Button chỉ có trên iPhone 15 Pro trở lên. DB hiện tại chỉ có thông tin về cần gạt rung/chuông của iPhone 14."
    )
    
    # Case 2: Hallucinations
    run_case(
        case_num=3,
        title="Ảo giác/Thông tin sai lệch",
        description="Ngăn chặn AI đồng tình với các giả định sai của người dùng",
        question="Hướng dẫn tôi cách bật tính năng máy chiếu (Projector) trên iPhone?",
        context_note="💡 Thực tế: iPhone chưa bao giờ có máy chiếu tích hợp."
    )
    
    # Case 3: Comparative
    run_case(
        case_num=4,
        title="So sánh dữ liệu cũ và mới",
        description="Xử lý câu hỏi yêu cầu kiến thức 'lai' giữa cái cũ (có trong DB) và cái mới (phải tìm bên ngoài)",
        question="Cổng sạc của iPhone 15 khác gì so với iPhone 14?",
        context_note="💡 DB chỉ có thông tin về iPhone 14 (Lightning), không có iPhone 15 (USB-C)."
    )
    
    st.markdown("---")
    
    # # Custom Query Section
    # st.header("Try Your Own Question")
    # st.markdown("Enter a custom question to compare Traditional RAG vs Corrective RAG")
    
    # # Text input for custom question
    # custom_question = st.text_input(
    #     "Your Question:",
    #     placeholder="Ví dụ: Cách sử dụng AirPlay trên iPhone?",
    #     key="custom_question_input"
    # )
    
    # Submit button
    # if st.button("🔍 Search", type="primary", use_container_width=True):
    #     if custom_question.strip():
    #         with st.spinner("Processing question..."):
    #             col1, col2 = st.columns(2)
                
    #             with col1:
    #                 st.subheader("🔵 Traditional RAG")
    #                 try:
    #                     trad_result = st.session_state.traditional_rag.query(custom_question)
                        
    #                     st.markdown("**Answer:**")
    #                     st.write(trad_result.get("answer", "Không có câu trả lời"))
                        
    #                     # Show source documents
    #                     with st.expander("📄 Source Documents"):
    #                         source_docs = trad_result.get("source_documents", [])
    #                         if source_docs:
    #                             for i, doc in enumerate(source_docs[:3], 1):
    #                                 source = doc.metadata.get('source', 'Unknown')
    #                                 st.markdown(f"**Document {i}:** `{Path(source).name}`")
    #                                 st.text(doc.page_content[:200] + "...")
    #                         else:
    #                             st.info("No documents retrieved")
    #                 except Exception as e:
    #                     st.error(f"Error: {e}")
                
    #             with col2:
    #                 st.subheader("🟢 Corrective RAG")
    #                 try:
    #                     crag_result = st.session_state.corrective_rag.query(
    #                         custom_question, 
    #                         k=4, 
    #                         return_diagnostics=True
    #                     )
                        
    #                     st.markdown("**Answer:**")
    #                     st.write(crag_result.get("answer", "Không có câu trả lời"))
                        
    #                     # Display diagnostics
    #                     display_diagnostics(crag_result)
                        
    #                     # Show relevant documents
    #                     with st.expander("📄 Relevant Documents"):
    #                         relevant_docs = crag_result.get("source_documents", [])
    #                         if relevant_docs:
    #                             for i, doc in enumerate(relevant_docs[:3], 1):
    #                                 source = doc.metadata.get('source', 'Unknown')
    #                                 st.markdown(f"**Document {i}:** `{Path(source).name}`")
    #                                 st.text(doc.page_content[:200] + "...")
    #                         else:
    #                             st.info("No relevant documents retained")
    #                 except Exception as e:
    #                     st.error(f"Error: {e}")
    #     else:
    #         st.warning("⚠️ Please enter a question!")

if __name__ == "__main__":
    main()


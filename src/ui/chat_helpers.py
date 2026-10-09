import html
import time
import streamlit as st

def _to_html(text):
    """Escape HTML (tránh lỗi/XSS) và giữ xuống dòng."""
    return html.escape(text).replace("\n", "<br>")


def user_bubble_html(content):
    return (
        '<div class="chat-bubble-container">'
        f'<div class="chat-bubble-user">{_to_html(content)}</div>'
        "</div>"
    )


def assistant_bubble_html(content, sources=None):
    sources_html = ""
    if sources:
        items = "".join(f"<li>{html.escape(s)}</li>" for s in sources)
        sources_html = (
            '<div class="source-box"><b>📚 Nguồn tài liệu:</b>'
            f'<ul style="margin: 4px 0 0 18px; padding: 0;">{items}</ul></div>'
        )
    return (
        '<div class="chat-bubble-container">'
        '<div class="chat-bubble-assistant">'
        f"🤖 <b>Chatbot:</b><br>{_to_html(content)}{sources_html}"
        "</div></div>"
    )


def stream_assistant_bubble(text, delay=0.04):
    """
    Hiển thị chữ chạy ra dần (streaming) trong bong bóng chat của chatbot.
    Dùng cho lời chào khi mở app.
    """
    # TODO [REAL CODE]: Khi gọi LLM thật, thay vòng lặp giả lập này bằng stream
    # token thật từ LlamaIndex, ví dụ:
    #   streaming_response = query_engine.query(question)   # query_engine tạo với streaming=True
    #   for token in streaming_response.response_gen:
    #       shown += token
    #       placeholder.markdown(assistant_bubble_html(shown + " ▌"), unsafe_allow_html=True)
    # Lời chào mở đầu có thể giữ nguyên là chuỗi cố định (không cần gọi LLM).
    placeholder = st.empty()
    shown = ""
    for word in text.split(" "):
        shown += word + " "
        placeholder.markdown(assistant_bubble_html(shown + "▌"), unsafe_allow_html=True)
        time.sleep(delay * max(1, len(word) // 3))
    # Bỏ con trỏ nhấp nháy khi stream xong
    placeholder.markdown(assistant_bubble_html(text), unsafe_allow_html=True)


# ============================================================
# MOCK RAG FUNCTION
# ============================================================


def mock_rag_answer(question, selected_group):
    """
    Giả lập phản hồi RAG tích hợp bộ lọc nhóm tài liệu.
    """
    # TODO [REAL CODE]: THAY TOÀN BỘ HÀM NÀY bằng pipeline RAG thật (LlamaIndex).
    # Các bước gợi ý:
    #
    # 1) Lấy index đã build sẵn (cache, không build lại mỗi lần hỏi):
    #       index = get_index()   # xem hàm get_index() ở mục INDEXING bên dưới
    #
    # 2) Lọc theo nhóm tài liệu người dùng chọn (selected_group):
    #       from llama_index.core.vector_stores import MetadataFilters, MetadataFilter
    #       filters = None
    #       if selected_group != "Tất cả tài liệu":
    #           filters = MetadataFilters(filters=[MetadataFilter(key="label", value=selected_group)])
    #
    # 3) Tạo query engine / chat engine:
    #       query_engine = index.as_query_engine(
    #           similarity_top_k=5, filters=filters, streaming=True
    #       )
    #       response = query_engine.query(question)
    #
    # 4) Lấy nguồn trích dẫn từ response.source_nodes:
    #       sources = sorted({n.node.metadata.get("file_name") for n in response.source_nodes})
    #       (có thể thêm số trang: n.node.metadata.get("page_label"), điểm: n.score)
    #
    # 5) Trả về (str(response), sources). Nếu muốn stream chữ ra, trả về
    #    response.response_gen để chat_page() hiển thị từng token.
    #
    # Lưu ý: nên đưa lịch sử hội thoại vào (ChatMemoryBuffer / condense question)
    # nếu muốn chatbot hiểu câu hỏi nối tiếp.
    question_lower = question.lower()

    if "học bổng" in question_lower:
        return (
            f"[Nhóm: {selected_group}] Theo quy định học bổng, sinh viên cần đạt GPA tối thiểu "
            "từ 3.2/4.0 và điểm rèn luyện loại Tốt trở lên.",
            ["quy-dinh-hoc-bong.pdf", "dieu-kien-hoc-bong.docx"],
        )

    if "tín chỉ" in question_lower:
        return (
            f"[Nhóm: {selected_group}] Theo quy chế đào tạo tín chỉ, sinh viên được đăng ký "
            "tối đa 24 tín chỉ và tối thiểu 12 tín chỉ trong một học kỳ chính.",
            ["quy-che-dao-tao.pdf"],
        )

    return (
        f"[Nhóm áp dụng: {selected_group}] Đây là câu trả lời thử nghiệm từ RAG system. "
        "Dữ liệu được truy vấn dựa trên chỉ mục LlamaIndex.",
        [],
    )



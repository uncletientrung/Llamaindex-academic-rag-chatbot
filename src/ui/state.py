import uuid
import streamlit as st
from src.ui import chat_history

DEFAULT_TITLE = "Cuộc trò chuyện mới"
GREETING_TEXT = "Xin chào bạn, cần giúp gì?"
def create_session():
    """Tạo 1 phiên chat mới (chưa chào -> sẽ tự stream lời chào khi mở)."""
    # TODO [REAL CODE]: Lưu phiên chat vào DB (SQLite/PostgreSQL/Redis)
    # thay vì chỉ giữ trong st.session_state (mất khi refresh trang).
    # Gợi ý bảng: sessions(id, user_id, title, created_at),
    #             messages(id, session_id, role, content, sources_json, created_at)
    new_id = str(uuid.uuid4())
    chat_history.create_session(new_id, DEFAULT_TITLE)
    st.session_state.sessions[new_id] = {
        "title": DEFAULT_TITLE,
        "messages": [],
        "greeted": False,  # cờ: đã stream lời chào chưa
    }
    return new_id


# ============================================================
# SESSION STATE INITIALIZATION
# ============================================================

def initialize_session_state():
    chat_history.initialize_database()
    if "sessions" not in st.session_state:
        st.session_state.sessions = chat_history.list_sessions()
        for session_id, session in st.session_state.sessions.items():
            session["messages"] = chat_history.get_messages(session_id)
            session["greeted"] = bool(session["messages"])
        if st.session_state.sessions:
            st.session_state.current_session_id = next(iter(st.session_state.sessions))
        else:
            st.session_state.sessions = {}
            st.session_state.current_session_id = create_session()

    if "labels" not in st.session_state:
        # TODO [REAL CODE]: Dữ liệu nhóm tài liệu (label -> danh sách file) đang là
        # dữ liệu giả. Khi làm thật, load từ DB / metadata store, ví dụ:
        #   labels = db.get_all_labels_with_files()
        st.session_state.labels = {
            "Quy định học bổng": [
                "quy-dinh-hoc-bong.pdf",
                "dieu-kien-hoc-bong.docx",
            ],
            "Quy định tín chỉ": [
                "quy-che-dao-tao.pdf",
            ],
            "Quy định học phí": [],
        }

    if "current_page" not in st.session_state:
        st.session_state.current_page = "Chat RAG"

    if "selected_document_group" not in st.session_state:
        st.session_state.selected_document_group = "Tất cả tài liệu"

    # Bộ đếm key cho file_uploader của từng nhóm.
    # Tăng số này để RESET uploader sau khi xử lý xong (tránh file bị thêm lại
    # sau khi người dùng vừa xóa nó).
    if "uploader_keys" not in st.session_state:
        st.session_state.uploader_keys = {}


import streamlit as st
from src.ui.state import DEFAULT_TITLE, GREETING_TEXT
from src.ui.chat_helpers import user_bubble_html, assistant_bubble_html, stream_assistant_bubble, mock_rag_answer
from src.ui import chat_history

def chat_page():
        st.markdown('<div class="main-title">💬 Hỏi đáp quy định học vụ</div>', unsafe_allow_html=True)
        st.caption(f"Đang tìm kiếm trong: **{st.session_state.selected_document_group}**")
        st.divider()
    
        # Lấy phiên hội thoại hiện tại
        curr_session_id = st.session_state.current_session_id
        if curr_session_id not in st.session_state.sessions:
            st.session_state.current_session_id = list(st.session_state.sessions.keys())[0]
            curr_session_id = st.session_state.current_session_id
    
        session = st.session_state.sessions[curr_session_id]
        current_messages = session["messages"]
    
        # Container chứa lịch sử tin nhắn dạng Messenger
        chat_container = st.container()
    
        with chat_container:
            for msg in current_messages:
                if msg["role"] == "user":
                    st.markdown(user_bubble_html(msg["content"]), unsafe_allow_html=True)
                else:
                    st.markdown(
                        assistant_bubble_html(msg["content"], msg.get("sources")),
                        unsafe_allow_html=True,
                    )
    
            # Lời chào tự động (streaming) khi phiên chat mới được mở lần đầu
            if not session.get("greeted"):
                stream_assistant_bubble(GREETING_TEXT)
                current_messages.append(
                    {"role": "assistant", "content": GREETING_TEXT, "sources": []}
                )
                chat_history.add_message(curr_session_id, "assistant", GREETING_TEXT)
                session["greeted"] = True
    
        # Chat Input
        question = st.chat_input("Nhập câu hỏi về quy định...")
        if question:
            # 1. Lưu câu hỏi user
            current_messages.append({"role": "user", "content": question})
            chat_history.add_message(curr_session_id, "user", question)
    
            # Tự động đặt tên tiêu đề chat dựa trên câu hỏi đầu tiên của user
            # (không dùng len(messages)==1 nữa vì tin nhắn chào đã nằm sẵn trong danh sách)
            if session["title"] == DEFAULT_TITLE:
                # TODO [REAL CODE]: Có thể nhờ LLM tóm tắt câu hỏi thành tiêu đề ngắn.
                session["title"] = question[:25] + "..." if len(question) > 25 else question
                chat_history.update_title(curr_session_id, session["title"])
    
            # 2. Gọi RAG mock
            # TODO [REAL CODE]: Thêm st.spinner("Đang tìm kiếm tài liệu...") và xử lý
            # exception (hết quota LLM, vector store lỗi, không tìm thấy tài liệu phù hợp...).
            answer, sources = mock_rag_answer(question, st.session_state.selected_document_group)
    
            # 3. Lưu câu trả lời assistant
            # TODO [REAL CODE]: Lưu cả câu hỏi và câu trả lời vào DB (bảng messages).
            current_messages.append({"role": "assistant", "content": answer, "sources": sources})
            chat_history.add_message(curr_session_id, "assistant", answer, sources)
    
            st.rerun()
    
    

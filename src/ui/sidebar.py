import streamlit as st
from src.ui.state import create_session
from src.ui import chat_history

def render_left_sidebar():
        with st.sidebar:
            st.markdown(
                """
                <div style="text-align:center;">
                    <h2 style="margin-top:0;">🎓 Academic RAG</h2>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.divider()
    
            # 1. Điều hướng trang
            st.caption("📌 ĐIỀU HƯỚNG")
            if st.button(
                "💬 Hỏi đáp RAG",
                use_container_width=True,
                type="primary" if st.session_state.current_page == "Chat RAG" else "secondary",
            ):
                st.session_state.current_page = "Chat RAG"
                st.rerun()
    
            if st.button(
                "📚 Quản lý tài liệu",
                use_container_width=True,
                type="primary" if st.session_state.current_page == "Documents" else "secondary",
            ):
                st.session_state.current_page = "Documents"
                st.rerun()
    
            st.divider()
    
            # 2. Phạm vi tìm kiếm
            st.caption("🔍 CHỌN NHÓM TÀI LIỆU TRUY VẤN")
            group_options = ["Tất cả tài liệu"] + list(st.session_state.labels.keys())
            st.session_state.selected_document_group = st.selectbox(
                "Phạm vi tìm kiếm:",
                options=group_options,
                index=(
                    0
                    if st.session_state.selected_document_group not in group_options
                    else group_options.index(st.session_state.selected_document_group)
                ),
                label_visibility="collapsed",
            )
    
            st.divider()
    
            # 3. Lịch sử Chat nằm ở sidebar bên trái
            st.caption("🕒 LỊCH SỬ CHAT")
    
            if st.button("➕ Cuộc trò chuyện mới", use_container_width=True, type="primary"):
                st.session_state.current_session_id = create_session()
                st.session_state.current_page = "Chat RAG"
                st.rerun()
    
            st.write("")
    
            # Hiển thị danh sách các phiên chat
            for sess_id, sess_data in list(st.session_state.sessions.items()):
                col_title, col_del = st.columns([4, 1])
    
                is_active = sess_id == st.session_state.current_session_id
                btn_label = f"💬 {sess_data['title']}"
    
                with col_title:
                    if st.button(
                        btn_label,
                        key=f"sess_{sess_id}",
                        use_container_width=True,
                        type="primary" if is_active else "secondary",
                    ):
                        st.session_state.current_session_id = sess_id
                        st.session_state.sessions[sess_id]["messages"] = chat_history.get_messages(sess_id)
                        st.session_state.sessions[sess_id]["greeted"] = bool(
                            st.session_state.sessions[sess_id]["messages"]
                        )
                        st.session_state.current_page = "Chat RAG"
                        st.rerun()
    
                with col_del:
                    if st.button("🗑️", key=f"del_sess_{sess_id}"):
                        chat_history.delete_session(sess_id)
                        del st.session_state.sessions[sess_id]
                        if not st.session_state.sessions:
                            st.session_state.current_session_id = create_session()
                        else:
                            st.session_state.current_session_id = list(
                                st.session_state.sessions.keys()
                            )[0]
                        st.rerun()
    
    

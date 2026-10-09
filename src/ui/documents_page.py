import streamlit as st

def documents_page():
        st.markdown('<div class="main-title">📚 Quản lý tài liệu</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="subtitle">Quản lý các nhóm tài liệu và tệp tin phục vụ RAG.</div>',
            unsafe_allow_html=True,
        )
    
        # 1. Tạo nhóm mới
        st.subheader("Tạo nhóm tài liệu mới")
        col1, col2 = st.columns([4, 1])
        with col1:
            new_label = st.text_input(
                "Tên nhóm",
                placeholder="Ví dụ: Quy định học phí",
                label_visibility="collapsed",
            )
        with col2:
            if st.button("➕ Tạo nhóm", use_container_width=True):
                if not new_label.strip():
                    st.warning("Tên nhóm không được để trống.")
                elif new_label in st.session_state.labels:
                    st.warning("Nhóm này đã tồn tại.")
                else:
                    # TODO [REAL CODE]: Lưu nhóm mới vào DB / metadata store
                    # (và tạo thư mục lưu file, vd ./data/<tên nhóm>/).
                    st.session_state.labels[new_label] = []
                    st.success(f"Đã tạo nhóm: {new_label}")
                    st.rerun()
    
        st.divider()
    
        # 2. Danh sách các nhóm & xóa file
        st.subheader("Danh sách nhóm tài liệu & Tệp tin")
        if not st.session_state.labels:
            st.info("Chưa có nhóm tài liệu nào.")
            return
    
        # TODO [REAL CODE]: Thêm nút "Xóa nhóm": xóa nhóm trong DB + xóa toàn bộ
        # chunk thuộc nhóm đó trong vector store (filter metadata label == tên nhóm).
    
        for label_name, files in list(st.session_state.labels.items()):
            with st.container(border=True):
                col_info, col_action = st.columns([3, 2])
    
                with col_info:
                    st.markdown(f"### 📁 {label_name}")
                    if files:
                        for idx, file_name in enumerate(files):
                            f_col1, f_col2 = st.columns([4, 1])
                            with f_col1:
                                st.markdown(f"📄 `{file_name}`")
                            with f_col2:
                                if st.button("🗑", key=f"del_{label_name}_{idx}", help=f"Xóa file {file_name}"):
                                    # TODO [REAL CODE]: Xóa file thật:
                                    #   1) xóa file gốc trên đĩa / S3
                                    #   2) xóa các chunk của file khỏi vector store
                                    #      -> delete_file_from_index(label_name, file_name)
                                    #   3) cập nhật DB metadata
                                    st.session_state.labels[label_name].remove(file_name)
                                    st.success(f"Đã xóa file `{file_name}`")
                                    st.rerun()
                    else:
                        st.caption("Chưa có tài liệu trong nhóm này.")
    
                with col_action:
                    # Key thay đổi sau mỗi lần upload -> uploader được reset sạch
                    up_key = st.session_state.uploader_keys.get(label_name, 0)
                    uploaded_files = st.file_uploader(
                        "Thêm file vào nhóm",
                        type=["pdf", "docx", "txt"],
                        accept_multiple_files=True,
                        key=f"upload_{label_name}_{up_key}",
                    )
                    if uploaded_files:
                        added_count = 0
                        for uploaded_file in uploaded_files:
                            if uploaded_file.name not in st.session_state.labels[label_name]:
                                # TODO [REAL CODE]: Thay dòng append tên file bên dưới bằng
                                # pipeline xử lý thật (xem mục INDEXING phía trên):
                                #   with st.spinner(f"Đang xử lý {uploaded_file.name}..."):
                                #       ingest_file(uploaded_file, label_name)
                                #       # = lưu file -> đọc nội dung -> chunking -> embedding -> index
                                # Nên xử lý lỗi (file hỏng, PDF scan không có text, file quá lớn...).
                                st.session_state.labels[label_name].append(uploaded_file.name)
                                added_count += 1
                        st.session_state.uploader_keys[label_name] = up_key + 1
                        if added_count > 0:
                            st.success(f"Đã thêm {added_count} file vào '{label_name}'")
                        st.rerun()
    
    

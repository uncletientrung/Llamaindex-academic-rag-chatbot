import streamlit as st
from datetime import datetime


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Academic RAG",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# SESSION STATE
# ============================================================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = ""

if "labels" not in st.session_state:
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

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "current_page" not in st.session_state:
    st.session_state.current_page = "Chat RAG"


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    /* ---------- Main ---------- */

    .main-title {
        font-size: 30px;
        font-weight: 700;
        margin-bottom: 5px;
    }

    .subtitle {
        color: #6b7280;
        margin-bottom: 25px;
    }

    /* ---------- Cards ---------- */

    .document-card {
        padding: 15px;
        border: 1px solid #e5e7eb;
        border-radius: 12px;
        margin-bottom: 12px;
        background-color: #ffffff;
    }

    .document-title {
        font-size: 17px;
        font-weight: 600;
        margin-bottom: 8px;
    }

    .file-item {
        color: #6b7280;
        font-size: 14px;
        padding: 3px 0;
    }

    /* ---------- Chat ---------- */

    .source-box {
        padding: 10px 14px;
        border-radius: 8px;
        background-color: #f8fafc;
        border: 1px solid #e5e7eb;
        font-size: 13px;
        color: #64748b;
        margin-top: 10px;
    }

    /* ---------- Login ---------- */

    .login-container {
        max-width: 450px;
        margin: 70px auto;
    }

    /* ---------- Hide Streamlit decoration ---------- */

    #MainMenu {
        visibility: hidden;
    }

    footer {
        visibility: hidden;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# MOCK RAG
# ============================================================

def mock_rag_answer(question):
    """
    Đây chỉ là dữ liệu giả để test giao diện.

    Sau này sẽ thay hàm này bằng:
        Retriever
            ↓
        Reranker
            ↓
        Response Synthesizer
            ↓
        LLM
    """

    question_lower = question.lower()

    if "học bổng" in question_lower:
        return (
            "Theo tài liệu quy định học bổng, sinh viên cần đáp ứng "
            "các điều kiện được quy định trong quy chế học bổng của nhà trường."
        ), [
            "quy-dinh-hoc-bong.pdf",
            "dieu-kien-hoc-bong.docx",
        ]

    if "tín chỉ" in question_lower:
        return (
            "Theo quy chế đào tạo, sinh viên đăng ký học phần dựa trên "
            "các điều kiện và giới hạn tín chỉ được quy định."
        ), [
            "quy-che-dao-tao.pdf",
        ]

    if "học phí" in question_lower:
        return (
            "Thông tin học phí được lấy từ nhóm tài liệu quy định học phí "
            "đã được tải lên hệ thống."
        ), [
            "quy-dinh-hoc-phi.pdf",
        ]

    return (
        "Đây là câu trả lời mẫu từ hệ thống RAG. "
        "Sau khi kết nối LlamaIndex, câu trả lời sẽ được sinh "
        "dựa trên các tài liệu đã tải lên."
    ), []


# ============================================================
# LOGIN PAGE
# ============================================================

def login_page():

    st.markdown(
        """
        <div class="login-container">
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div style="text-align:center;">
            <div style="font-size:55px;">🎓</div>
            <div class="main-title">Academic RAG</div>
            <div class="subtitle">
                Chatbot tra cứu quy định học vụ
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.form("login_form"):

        username = st.text_input(
            "Tên đăng nhập",
            placeholder="Nhập tên đăng nhập",
        )

        password = st.text_input(
            "Mật khẩu",
            type="password",
            placeholder="Nhập mật khẩu",
        )

        submitted = st.form_submit_button(
            "Đăng nhập",
            use_container_width=True,
            type="primary",
        )

        if submitted:

            if username and password:

                st.session_state.logged_in = True
                st.session_state.username = username

                st.rerun()

            else:

                st.error(
                    "Vui lòng nhập đầy đủ tên đăng nhập và mật khẩu."
                )

    st.markdown("</div>", unsafe_allow_html=True)


# ============================================================
# SIDEBAR
# ============================================================

def render_sidebar():

    with st.sidebar:

        st.markdown(
            """
            <div style="text-align:center;">
                <div style="font-size:42px;">🎓</div>
                <h2 style="margin-top:0;">Academic RAG</h2>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.divider()

        st.caption("ĐIỀU HƯỚNG")

        if st.button(
            "💬  Hỏi đáp RAG",
            use_container_width=True,
        ):
            st.session_state.current_page = "Chat RAG"
            st.rerun()

        if st.button(
            "📚  Quản lý tài liệu",
            use_container_width=True,
        ):
            st.session_state.current_page = "Documents"
            st.rerun()

        if st.button(
            "🕘  Lịch sử hỏi đáp",
            use_container_width=True,
        ):
            st.session_state.current_page = "History"
            st.rerun()

        st.divider()

        st.caption("TÀI KHOẢN")

        st.write(f"👤 **{st.session_state.username}**")

        if st.button(
            "🚪  Đăng xuất",
            use_container_width=True,
        ):
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.session_state.current_page = "Chat RAG"
            st.rerun()


# ============================================================
# DOCUMENT PAGE
# ============================================================

def documents_page():

    st.markdown(
        '<div class="main-title">📚 Quản lý tài liệu</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="subtitle">'
        'Tạo nhóm tài liệu theo từng loại quy định và tải nhiều file vào mỗi nhóm.'
        '</div>',
        unsafe_allow_html=True,
    )

    # --------------------------------------------------------
    # CREATE LABEL
    # --------------------------------------------------------

    st.subheader("Tạo nhóm tài liệu")

    col1, col2 = st.columns([4, 1])

    with col1:

        new_label = st.text_input(
            "Tên nhóm / Label",
            placeholder="Ví dụ: Quy định học bổng",
            label_visibility="collapsed",
        )

    with col2:

        create_label = st.button(
            "➕ Tạo label",
            use_container_width=True,
        )

    if create_label:

        if not new_label.strip():

            st.warning("Vui lòng nhập tên label.")

        elif new_label in st.session_state.labels:

            st.warning("Label này đã tồn tại.")

        else:

            st.session_state.labels[new_label] = []

            st.success(
                f"Đã tạo label: {new_label}"
            )

            st.rerun()

    st.divider()

    # --------------------------------------------------------
    # LABELS
    # --------------------------------------------------------

    st.subheader("Các nhóm tài liệu")

    if not st.session_state.labels:

        st.info("Chưa có nhóm tài liệu.")

        return

    for label, files in st.session_state.labels.items():

        with st.container(border=True):

            col1, col2 = st.columns([4, 1])

            with col1:

                st.markdown(
                    f"### 📁 {label}"
                )

                if files:

                    for file_name in files:

                        st.markdown(
                            f"📄 `{file_name}`"
                        )

                else:

                    st.caption(
                        "Chưa có tài liệu."
                    )

            with col2:

                st.write("")

                upload_key = f"upload_{label}"

                uploaded_files = st.file_uploader(
                    "Upload",
                    type=["pdf", "docx"],
                    accept_multiple_files=True,
                    key=upload_key,
                    label_visibility="collapsed",
                )

            if uploaded_files:

                new_files = []

                for uploaded_file in uploaded_files:

                    if uploaded_file.name not in files:

                        new_files.append(
                            uploaded_file.name
                        )

                if new_files:

                    st.session_state.labels[label].extend(
                        new_files
                    )

                    st.success(
                        f"Đã thêm {len(new_files)} file vào "
                        f"'{label}'."
                    )

                    st.rerun()


# ============================================================
# CHAT PAGE
# ============================================================

def chat_page():

    st.markdown(
        '<div class="main-title">💬 Hỏi đáp quy định học vụ</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="subtitle">'
        'Đặt câu hỏi và hệ thống RAG sẽ tìm kiếm thông tin '
        'từ các tài liệu nội bộ.'
        '</div>',
        unsafe_allow_html=True,
    )

    # --------------------------------------------------------
    # SHOW CHAT HISTORY
    # --------------------------------------------------------

    for message in st.session_state.chat_history:

        role = message["role"]

        with st.chat_message(role):

            st.markdown(
                message["content"]
            )

            if (
                role == "assistant"
                and message.get("sources")
            ):

                st.markdown(
                    '<div class="source-box">'
                    '📚 <b>Nguồn tham khảo</b><br>'
                    + "<br>".join(
                        [
                            f"• {source}"
                            for source in message["sources"]
                        ]
                    )
                    + "</div>",
                    unsafe_allow_html=True,
                )

    # --------------------------------------------------------
    # CHAT INPUT
    # --------------------------------------------------------

    question = st.chat_input(
        "Nhập câu hỏi về quy định học vụ..."
    )

    if question:

        # User message

        st.session_state.chat_history.append(
            {
                "role": "user",
                "content": question,
            }
        )

        # Mock RAG

        answer, sources = mock_rag_answer(
            question
        )

        # Assistant message

        st.session_state.chat_history.append(
            {
                "role": "assistant",
                "content": answer,
                "sources": sources,
            }
        )

        st.rerun()


# ============================================================
# HISTORY PAGE
# ============================================================

def history_page():

    st.markdown(
        '<div class="main-title">🕘 Lịch sử hỏi đáp</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="subtitle">'
        'Các câu hỏi và câu trả lời trước đây.'
        '</div>',
        unsafe_allow_html=True,
    )

    user_messages = [
        message
        for message in st.session_state.chat_history
        if message["role"] == "user"
    ]

    if not user_messages:

        st.info(
            "Bạn chưa có lịch sử hỏi đáp."
        )

        return

    for index, message in enumerate(
        user_messages,
        start=1,
    ):

        with st.container(border=True):

            st.markdown(
                f"**{index}. 💬 {message['content']}**"
            )

            st.caption(
                "Cuộc trò chuyện hiện tại"
            )

    st.divider()

    if st.button(
        "🗑️ Xóa lịch sử",
        type="secondary",
    ):

        st.session_state.chat_history = []

        st.success(
            "Đã xóa lịch sử."
        )

        st.rerun()


# ============================================================
# MAIN APP
# ============================================================

if not st.session_state.logged_in:

    login_page()

else:

    render_sidebar()

    if st.session_state.current_page == "Chat RAG":

        chat_page()

    elif st.session_state.current_page == "Documents":

        documents_page()

    elif st.session_state.current_page == "History":

        history_page()


import html
import time
import uuid

import streamlit as st

# ============================================================
# QUY ƯỚC CHÚ THÍCH TRONG FILE NÀY
# ------------------------------------------------------------
# Đây là bản DEMO (dữ liệu giả lập). Mọi chỗ cần thay bằng code thật
# đều được đánh dấu bằng tag:   # TODO [REAL CODE]
# Tìm nhanh bằng Ctrl+F "TODO [REAL CODE]" để xem toàn bộ danh sách.
# ============================================================

DEFAULT_TITLE = "Cuộc trò chuyện mới"
GREETING_TEXT = "Xin chào bạn, cần giúp gì?"

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
# HELPERS: TẠO PHIÊN CHAT
# ============================================================


def create_session():
    """Tạo 1 phiên chat mới (chưa chào -> sẽ tự stream lời chào khi mở)."""
    # TODO [REAL CODE]: Lưu phiên chat vào DB (SQLite/PostgreSQL/Redis)
    # thay vì chỉ giữ trong st.session_state (mất khi refresh trang).
    # Gợi ý bảng: sessions(id, user_id, title, created_at),
    #             messages(id, session_id, role, content, sources_json, created_at)
    new_id = str(uuid.uuid4())
    st.session_state.sessions[new_id] = {
        "title": DEFAULT_TITLE,
        "messages": [],
        "greeted": False,  # cờ: đã stream lời chào chưa
    }
    return new_id


# ============================================================
# SESSION STATE INITIALIZATION
# ============================================================

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

# Quản lý nhiều phiên chat (ChatGPT style)
if "sessions" not in st.session_state:
    st.session_state.sessions = {}
    st.session_state.current_session_id = create_session()

if "current_page" not in st.session_state:
    st.session_state.current_page = "Chat RAG"

if "selected_document_group" not in st.session_state:
    st.session_state.selected_document_group = "Tất cả tài liệu"

# Bộ đếm key cho file_uploader của từng nhóm.
# Tăng số này để RESET uploader sau khi xử lý xong (tránh file bị thêm lại
# sau khi người dùng vừa xóa nó).
if "uploader_keys" not in st.session_state:
    st.session_state.uploader_keys = {}

# ============================================================
# CUSTOM CSS - Bảng màu chuẩn (mục 5.1.1)
# ------------------------------------------------------------
#   Primary   : #007BFF  (Blue)        - Buttons, highlights
#   Secondary : #FFC107  (Amber)       - Upload buttons
#   Background: #F8F9FA  (Light gray)  - Nền chính
#   Sidebar   : #2C2F33  (Dark gray)   - Nền sidebar
#   Text      : #212529  (Dark gray)   - Chữ chính
#   Sidebar Tx: #FFFFFF  (White)       - Chữ sidebar
# ============================================================

st.markdown(
    """
    <style>

    /* ---------- Design tokens ---------- */
    :root {
        --primary: #007BFF;
        --primary-hover: #0069D9;
        --secondary: #FFC107;
        --secondary-hover: #E0A800;
        --bg: #F8F9FA;
        --sidebar-bg: #2C2F33;
        --text: #212529;
        --sidebar-text: #FFFFFF;
        --border: #DEE2E6;
        --sidebar-width: 340px;
    }

    /* ---------- Nền & chữ chính ---------- */
    .stApp,
    [data-testid="stAppViewContainer"],
    [data-testid="stMain"] {
        background-color: var(--bg);
        color: var(--text);
    }

    [data-testid="stHeader"] {
        background: transparent;
    }

    [data-testid="stMain"] h1,
    [data-testid="stMain"] h2,
    [data-testid="stMain"] h3,
    [data-testid="stMain"] p,
    [data-testid="stMain"] label,
    [data-testid="stMain"] li {
        color: var(--text);
    }

    .main-title {
        font-size: 26px;
        font-weight: 700;
        margin-bottom: 5px;
        color: var(--text);
    }

    .subtitle {
        color: #6c757d;
        margin-bottom: 20px;
    }

    /* ---------- SIDEBAR (rộng hơn + nền tối + chữ trắng) ---------- */
    section[data-testid="stSidebar"][aria-expanded="true"] {
        width: var(--sidebar-width) !important;
        min-width: var(--sidebar-width) !important;
    }

    section[data-testid="stSidebar"] {
        background-color: var(--sidebar-bg);
    }

    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] [data-testid="stCaptionContainer"] {
        color: var(--sidebar-text) !important;
    }

    section[data-testid="stSidebar"] [data-testid="stCaptionContainer"] {
        opacity: 0.75;
        letter-spacing: 0.04em;
    }

    section[data-testid="stSidebar"] hr {
        border-color: rgba(255, 255, 255, 0.15);
    }

    /* Nút thường (secondary) trong sidebar: trong suốt, viền mờ */
    section[data-testid="stSidebar"] [data-testid="stBaseButton-secondary"],
    section[data-testid="stSidebar"] button[kind="secondary"] {
        background-color: transparent;
        color: var(--sidebar-text);
        border: 1px solid rgba(255, 255, 255, 0.25);
    }

    section[data-testid="stSidebar"] [data-testid="stBaseButton-secondary"]:hover,
    section[data-testid="stSidebar"] button[kind="secondary"]:hover {
        background-color: rgba(255, 255, 255, 0.08);
        border-color: var(--primary);
        color: var(--sidebar-text);
    }

    /* Selectbox trong sidebar */
    section[data-testid="stSidebar"] [data-baseweb="select"] > div {
        background-color: #3A3E44;
        border: 1px solid rgba(255, 255, 255, 0.25);
        color: var(--sidebar-text);
    }

    section[data-testid="stSidebar"] [data-baseweb="select"] svg {
        fill: var(--sidebar-text);
    }

    /* ---------- BUTTONS (Primary = #007BFF) ---------- */
    [data-testid="stBaseButton-primary"],
    button[kind="primary"] {
        background-color: var(--primary);
        border: 1px solid var(--primary);
        color: #FFFFFF;
    }

    [data-testid="stBaseButton-primary"]:hover,
    button[kind="primary"]:hover {
        background-color: var(--primary-hover);
        border-color: var(--primary-hover);
        color: #FFFFFF;
    }

    /* Nút thường ở vùng nội dung chính */
    [data-testid="stMain"] [data-testid="stBaseButton-secondary"] {
        background-color: #FFFFFF;
        color: var(--primary);
        border: 1px solid var(--primary);
    }

    [data-testid="stMain"] [data-testid="stBaseButton-secondary"]:hover {
        background-color: var(--primary);
        color: #FFFFFF;
    }

    /* ---------- UPLOAD BUTTON (Secondary = #FFC107) ---------- */
    [data-testid="stFileUploader"] button,
    [data-testid="stFileUploaderDropzone"] button {
        background-color: var(--secondary);
        color: var(--text);
        border: 1px solid var(--secondary);
        font-weight: 600;
    }

    [data-testid="stFileUploader"] button:hover,
    [data-testid="stFileUploaderDropzone"] button:hover {
        background-color: var(--secondary-hover);
        border-color: var(--secondary-hover);
        color: var(--text);
    }

    [data-testid="stFileUploaderDropzone"] {
        background-color: #FFFFFF;
        border: 1px dashed var(--secondary);
    }

    /* ---------- Container có viền (card nhóm tài liệu) ---------- */
    [data-testid="stMain"] [data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #FFFFFF;
        border-color: var(--border);
    }

    /* ---------- Messenger Style Chat Bubbles ---------- */
    .chat-bubble-container {
        display: flex;
        flex-direction: column;
        margin-bottom: 12px;
    }

    /* User Message - Right Aligned (Primary blue) */
    .chat-bubble-user {
        align-self: flex-end;
        background-color: var(--primary);
        color: #FFFFFF;
        padding: 10px 16px;
        border-radius: 18px 18px 2px 18px;
        max-width: 70%;
        word-wrap: break-word;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.12);
        margin-left: auto;
    }

    /* Assistant Message - Left Aligned (trắng, chữ tối) */
    .chat-bubble-assistant {
        align-self: flex-start;
        background-color: #FFFFFF;
        color: var(--text);
        border: 1px solid var(--border);
        padding: 12px 16px;
        border-radius: 18px 18px 18px 2px;
        max-width: 80%;
        word-wrap: break-word;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
        margin-right: auto;
    }

    .source-box {
        margin-top: 8px;
        padding: 8px 12px;
        border-radius: 8px;
        background-color: var(--bg);
        border: 1px solid var(--border);
        border-left: 3px solid var(--primary);
        font-size: 12px;
        color: var(--text);
    }

    /* Ô nhập chat */
    [data-testid="stChatInput"] {
        border-color: var(--primary);
    }

    /* ---------- Ẩn UI mặc định của Streamlit ---------- */
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# HTML HELPERS CHO BONG BÓNG CHAT
# ============================================================


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


# ============================================================
# INDEXING (CHƯA CÓ TRONG DEMO - CHỖ ĐỂ VIẾT CODE THẬT)
# ============================================================
# TODO [REAL CODE]: Pipeline xử lý tài liệu. Demo hiện chỉ lưu TÊN file vào
# session_state, chưa đọc nội dung, chưa chunking, chưa embedding.
# Khi làm thật, tách thành module riêng (vd: rag/ingest.py) với các hàm dưới đây.
#
# @st.cache_resource
# def get_index():
#     """Load / kết nối vector store 1 lần duy nhất cho cả app."""
#     import chromadb
#     from llama_index.core import VectorStoreIndex, StorageContext, Settings
#     from llama_index.vector_stores.chroma import ChromaVectorStore
#     from llama_index.embeddings.huggingface import HuggingFaceEmbedding
#     from llama_index.llms.openai import OpenAI
#
#     Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-m3")  # hỗ trợ tiếng Việt tốt
#     Settings.llm = OpenAI(model="gpt-4o-mini")                              # hoặc LLM bạn chọn
#
#     client = chromadb.PersistentClient(path="./chroma_db")
#     collection = client.get_or_create_collection("academic_docs")
#     vector_store = ChromaVectorStore(chroma_collection=collection)
#     storage_context = StorageContext.from_defaults(vector_store=vector_store)
#     return VectorStoreIndex.from_vector_store(vector_store, storage_context=storage_context)
#
#
# def ingest_file(uploaded_file, label):
#     """Xử lý 1 file được upload: lưu -> đọc -> chunking -> embedding -> index."""
#     # BƯỚC 1: Lưu file gốc xuống đĩa / S3 (uploaded_file.getbuffer())
#     #         vd: path = f"./data/{label}/{uploaded_file.name}"
#     #
#     # BƯỚC 2: Đọc nội dung (loader)
#     #         from llama_index.core import SimpleDirectoryReader
#     #         docs = SimpleDirectoryReader(input_files=[path]).load_data()
#     #         (PDF scan cần OCR; PDF/DOCX có bảng biểu có thể dùng LlamaParse)
#     #
#     # BƯỚC 3: Gắn metadata để lọc theo nhóm và trích dẫn nguồn
#     #         for d in docs:
#     #             d.metadata["label"] = label
#     #             d.metadata["file_name"] = uploaded_file.name
#     #
#     # BƯỚC 4: Chunking (chia nhỏ văn bản)
#     #         from llama_index.core.node_parser import SentenceSplitter
#     #         splitter = SentenceSplitter(chunk_size=512, chunk_overlap=64)
#     #         nodes = splitter.get_nodes_from_documents(docs)
#     #
#     # BƯỚC 5: Embedding + lưu vào vector store
#     #         get_index().insert_nodes(nodes)
#
#
# def delete_file_from_index(label, file_name):
#     """Xóa toàn bộ chunk của 1 file khỏi vector store + xóa file gốc trên đĩa."""
#     # vd (Chroma): collection.delete(where={"file_name": file_name, "label": label})
#     # hoặc index.delete_ref_doc(ref_doc_id, delete_from_docstore=True)


# ============================================================
# LEFT SIDEBAR (Điều hướng + Phạm vi tìm kiếm + Lịch sử Chat)
# ============================================================


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
                    st.session_state.current_page = "Chat RAG"
                    st.rerun()

            with col_del:
                if st.button("🗑️", key=f"del_sess_{sess_id}"):
                    # TODO [REAL CODE]: Xóa phiên chat khỏi DB (nếu đã lưu DB).
                    del st.session_state.sessions[sess_id]
                    if not st.session_state.sessions:
                        st.session_state.current_session_id = create_session()
                    else:
                        st.session_state.current_session_id = list(
                            st.session_state.sessions.keys()
                        )[0]
                    st.rerun()


# ============================================================
# DOCUMENT MANAGEMENT PAGE
# ============================================================


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


# ============================================================
# CHAT PAGE
# ============================================================


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
            session["greeted"] = True

    # Chat Input
    question = st.chat_input("Nhập câu hỏi về quy định...")
    if question:
        # 1. Lưu câu hỏi user
        current_messages.append({"role": "user", "content": question})

        # Tự động đặt tên tiêu đề chat dựa trên câu hỏi đầu tiên của user
        # (không dùng len(messages)==1 nữa vì tin nhắn chào đã nằm sẵn trong danh sách)
        if session["title"] == DEFAULT_TITLE:
            # TODO [REAL CODE]: Có thể nhờ LLM tóm tắt câu hỏi thành tiêu đề ngắn.
            session["title"] = question[:25] + "..." if len(question) > 25 else question

        # 2. Gọi RAG mock
        # TODO [REAL CODE]: Thêm st.spinner("Đang tìm kiếm tài liệu...") và xử lý
        # exception (hết quota LLM, vector store lỗi, không tìm thấy tài liệu phù hợp...).
        answer, sources = mock_rag_answer(question, st.session_state.selected_document_group)

        # 3. Lưu câu trả lời assistant
        # TODO [REAL CODE]: Lưu cả câu hỏi và câu trả lời vào DB (bảng messages).
        current_messages.append({"role": "assistant", "content": answer, "sources": sources})

        st.rerun()


# ============================================================
# MAIN ROUTING
# ============================================================

# TODO [REAL CODE]: Thêm đăng nhập / phân quyền nếu cần (vd: streamlit-authenticator)
# để mỗi người dùng chỉ thấy lịch sử chat và nhóm tài liệu của mình.

# Hiển thị Sidebar Trái (Chứa Navigation, Nhóm tài liệu & Lịch sử chat)
render_left_sidebar()

# Hiển thị trang tương ứng
if st.session_state.current_page == "Chat RAG":
    chat_page()
elif st.session_state.current_page == "Documents":
    documents_page()
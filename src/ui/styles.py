import streamlit as st

def apply_styles():
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
    
    

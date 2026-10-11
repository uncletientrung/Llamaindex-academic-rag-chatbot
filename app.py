"""Streamlit entry point. UI pages live under src/ui; domain services stay separate."""
import streamlit as st

from src.ui.chat_page import chat_page
from src.ui.documents_page import documents_page
from src.ui.sidebar import render_left_sidebar
from src.ui.state import initialize_session_state
from src.ui.styles import apply_styles

st.set_page_config(
    page_title="Academic RAG",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)
initialize_session_state()
apply_styles()
render_left_sidebar()

if st.session_state.current_page == "Chat RAG":
    chat_page()
elif st.session_state.current_page == "Documents":
    documents_page()

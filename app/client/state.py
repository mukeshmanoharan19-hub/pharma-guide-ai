from app.core.config import settings
import streamlit as st

from app.client.api import load_token


def init_session() -> None:
    backend_url = settings.BACKEND_URL
    if not backend_url:
        try:
            backend_url = st.secrets.get("BACKEND_URL", settings.BACKEND_URL)
        except Exception:
            backend_url = "http://localhost:8000"
    
    defaults = {
        "backend_url": backend_url,
        "auth_token": None,
        "user_email": None,
        "user_full_name": None,
        "messages": [],
        "error_message": None,
        "success_message": None,
        "pending_response": False,
        "pending_query": "",
        "stream_complete": False,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value
    
    # Try to load saved token from storage
    if not st.session_state.auth_token:
        saved = load_token()
        if saved:
            st.session_state.auth_token = saved.get("access_token")
            st.session_state.user_email = saved.get("email")

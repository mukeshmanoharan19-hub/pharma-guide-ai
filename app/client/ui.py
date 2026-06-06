import json

import streamlit as st

from app.client.api import ask, ask_stream, login, register, save_token, delete_token
from app.client.state import init_session


def render_style() -> None:
    st.markdown(
        """
        <style>
            .app-header {
                border-radius: 24px;
                padding: 32px;
                background: linear-gradient(135deg, #5b86e5 0%, #36d1dc 100%);
                color: white;
                margin-bottom: 24px;
            }
            .section-card {
                border-radius: 24px;
                padding: 24px;
                background: #ffffff;
                box-shadow: 0 16px 40px rgba(12, 47, 93, 0.08);
            }
            .streamlit-expanderHeader {
                font-weight: 700;
            }
            .footer-note {
                color: #6e7b94;
                font-size: 0.95rem;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def show_messages() -> None:
    for message in st.session_state.messages:
        if message["type"] == "user":
            st.chat_message("user").write(message["text"])
        else:
            with st.chat_message("assistant"):
                st.markdown(message["text"])
                products = message.get("products", [])
                if products:
                    st.markdown("**Suggested products:**")
                    for product in products:
                        cols = st.columns([1, 3])
                        image_url = product.get("image_url")
                        if image_url:
                            cols[0].image(image_url, width=120)
                        cols[1].markdown(
                            f"**{product.get('name', '')}**\n\n"
                            f"{product.get('description', '')}\n\n"
                            f"SKU: {product.get('sku', '')}  \n"
                            f"Price: ₹{product.get('price', '')}"
                        )


def login_form() -> None:
    with st.form(key="login_form", clear_on_submit=False):
        st.subheader("Login to Pharma Guide AI")
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_password")
        submitted = st.form_submit_button("Login")

    if submitted:
        st.session_state.error_message = None
        try:
            response = login(email, password, st.session_state.backend_url)
            st.session_state.auth_token = response["access_token"]
            st.session_state.user_email = email
            save_token(response["access_token"], email)
            st.session_state.success_message = "Logged in successfully. Start chatting now."
            st.rerun()
        except RuntimeError as error:
            st.session_state.error_message = str(error)


def signup_form() -> None:
    with st.form(key="signup_form", clear_on_submit=False):
        st.subheader("Create a new account")
        full_name = st.text_input("Full name", key="signup_name")
        email = st.text_input("Email", key="signup_email")
        password = st.text_input("Password", type="password", key="signup_password")
        confirm_password = st.text_input("Confirm password", type="password", key="signup_confirm")
        submitted = st.form_submit_button("Sign up")

    if submitted:
        st.session_state.error_message = None
        if password != confirm_password:
            st.session_state.error_message = "Passwords do not match."
            return
        try:
            register(full_name, email, password, st.session_state.backend_url)
            st.success("Account created successfully. Please log in.")
            st.session_state.success_message = "Account created — log in with your new credentials."
        except RuntimeError as error:
            st.session_state.error_message = str(error)


def chat_interface() -> None:
    st.markdown(
        f"### Hi, {st.session_state.user_email or 'pharma explorer'} 👋"
        "\n\nAsk anything about medicines, prescriptions, or health guidance."
    )

    if st.session_state.error_message:
        st.error(st.session_state.error_message)
        st.session_state.error_message = None
    if st.session_state.success_message:
        st.success(st.session_state.success_message)
        st.session_state.success_message = None

    with st.expander("Conversation settings", expanded=False):
        st.write("You are connected to the backend chat API.")
        st.text_input("Backend URL", value=st.session_state.backend_url, key="backend_url_input")
        if st.button("Update backend URL"):
            st.session_state.backend_url = st.session_state.backend_url_input
            st.success("Backend URL updated.")

    show_messages()

    if st.session_state.pending_response and not st.session_state.stream_complete:
        status_area = st.empty()
        status_area.info("Assistant is typing...",
                         icon="⌛")
        response_area = st.empty()
        full_response = ""

        try:
            for chunk in ask_stream(
                st.session_state.pending_query,
                st.session_state.backend_url,
                token=st.session_state.auth_token,
            ):
                full_response += chunk
                # Parse JSON and display only the answer field during streaming
                try:
                    parsed = json.loads(full_response)
                    answer_text = parsed.get("answer", full_response)
                    response_area.markdown(answer_text + "▌")
                except json.JSONDecodeError:
                    # If not complete JSON yet, show what we have
                    response_area.markdown(full_response + "▌")

            response_area.empty()
            
            assistant_text = full_response
            products = []
            try:
                parsed = json.loads(full_response)
                assistant_text = parsed.get("answer", full_response)
                products = parsed.get("productsSuggestions", [])
                st.markdown(assistant_text)
                
                if products:
                    st.markdown("**Suggested products:**")
                    for product in products:
                        cols = st.columns([1, 3])
                        image_url = product.get("image_url")
                        if image_url:
                            cols[0].image(image_url, width=120)
                        cols[1].markdown(
                            f"**{product.get('name', '')}**\n\n"
                            f"{product.get('description', '')}\n\n"
                            f"SKU: {product.get('sku', '')}  \n"
                            f"Price: ₹{product.get('price', '')}"
                        )
            except json.JSONDecodeError:
                st.markdown(full_response)

            st.session_state.messages.append({"type": "assistant", "text": assistant_text, "products": products})
            st.session_state.pending_response = False
            st.session_state.stream_complete = True
            st.session_state.pending_query = ""
            st.rerun()
        except RuntimeError as error:
            st.session_state.error_message = str(error)
            st.session_state.pending_response = False
            st.session_state.stream_complete = False
            st.session_state.pending_query = ""
            st.rerun()

    with st.form(key="chat_form", clear_on_submit=True):
        user_input = st.text_input("Type a message...", key="chat_input")
        submitted = st.form_submit_button("Send")

    if submitted and user_input:
        st.session_state.messages.append({"type": "user", "text": user_input, "products": []})
        st.session_state.pending_response = True
        st.session_state.pending_query = user_input
        st.session_state.stream_complete = False
        st.rerun()


def main() -> None:
    st.set_page_config(page_title="Pharma Guide AI", page_icon="💊", layout="wide")
    init_session()
    render_style()

    st.markdown(
        """
        <div class="app-header">
            <h1>Pharma Guide AI</h1>
            <p>Your secure medicine assistant with login-backed chat.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    columns = st.columns([2, 1])
    with columns[0]:
        if not st.session_state.auth_token:
            tabs = st.tabs(["Login", "Sign up"])
            with tabs[0]:
                login_form()
            with tabs[1]:
                signup_form()
        else:
            chat_interface()

    with columns[1]:
        st.markdown("<div class='section-card'>", unsafe_allow_html=True)
        st.subheader("Why use Pharma Guide AI")
        st.write(
            "- Login/signup secured by your FastAPI backend.\n"
            "- Chat with the `/api/chat/ask` endpoint.\n"
            "- Keep your medical Q&A workflow in one place."
        )
        if st.session_state.auth_token:
            if st.button("Logout"):
                st.session_state.auth_token = None
                st.session_state.user_email = None
                st.session_state.messages = []
                delete_token()
                st.session_state.success_message = "Logged out successfully."
                st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(
        "<p class='footer-note'>Need your backend on `http://localhost:8000`? Run it before opening this app.</p>",
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()

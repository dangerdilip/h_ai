import streamlit as st
import time

# Essential Configuration
st.set_page_config(page_title="H AI", page_icon="🤖", layout="wide")

hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            header {visibility: hidden;}
            footer {visibility: hidden;}
            
            /* Hide the bottom-right corner manage/deploy buttons & badges */
            .stAppDeployButton {display:none !important;}
            div[data-testid="stAppDeployButton"] {display:none !important;}
            [data-testid="manage-app-button"] {display:none !important;}
            [data-testid="viewerBadge"] {display:none !important;}
            #stDeployButton {display:none !important;}
            .stDeployButton {display:none !important;}
            .viewerBadge_container {display:none !important;}
            .viewerBadge_link {display:none !important;}
            div[data-testid="stToolbar"] {display:none !important;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

from components.splash_screen import check_splash_screen
from components.sidebar import render_sidebar
from components.chat_ui import render_chat_messages
from components.input_bar import render_quick_actions
from utils.gemini_client import initialize_gemini, get_system_prompt, get_response
from utils.groq_client import initialize_groq, get_groq_response
from utils.image_handler import load_image
from utils.url_fetcher import fetch_url_text
from utils.file_parser import process_file_upload

# 1. Start Animation Hook
if check_splash_screen():
    st.stop()

# Initialize API
initialize_gemini()
try:
    initialize_groq()
except Exception:
    pass # Wait for user to add secrets on Cloud

# Initialize memory
if "messages" not in st.session_state:
    st.session_state.messages = []

if "is_hardik" not in st.session_state:
    st.session_state.is_hardik = False

if st.session_state.is_hardik:
    golden_css = """
    <style>
    /* Golden Theme Overrides */
    .stApp { background: linear-gradient(135deg, #2a2000 0%, #171100 100%) !important; }
    .stSidebar { background-color: #140f00 !important; }
    div[data-testid="stChatMessage"] { background-color: #2a2000 !important; border: 1px solid #ffd700 !important; }
    h1, h2, h3, p, span, div { color: #fdf5e6 !important; }
    .stChatInputContainer > div { border: 1px solid #ffd700 !important; background-color: #1a1400 !important; }
    
    /* Golden Button Style */
    div.stButton > button:first-child {
        background-color: #ffd700 !important;
        color: #1a1400 !important;
        border: 1px solid #ffd700 !important;
        font-weight: bold !important;
        border-radius: 8px !important;
        box-shadow: 0 4px 6px rgba(255, 215, 0, 0.4) !important;
        transition: all 0.3s ease !important;
    }
    div.stButton > button:first-child:hover {
        background-color: #1a1400 !important;
        color: #ffd700 !important;
        border: 1px solid #ffd700 !important;
        box-shadow: 0 4px 12px rgba(255, 215, 0, 0.8) !important;
    }
    </style>
    """
    st.markdown(golden_css, unsafe_allow_html=True)

# Layout UI
render_sidebar()

# Main Chat View
st.title("H AI")
st.caption("Your Personal Multimodal Assistant")

# Render existing messages
render_chat_messages(st.session_state.messages)

# Prompt Templates at the bottom above chat input
quick_prompt = render_quick_actions()

# Chat Input
user_input_raw = st.chat_input("Ask me anything... (Type your message here)", accept_file="multiple")

user_text = ""
chat_files = []

if user_input_raw:
    if hasattr(user_input_raw, "text") and user_input_raw.text:
        user_text = user_input_raw.text
    elif isinstance(user_input_raw, str):
        user_text = str(user_input_raw)
        
    if hasattr(user_input_raw, "files") and user_input_raw.files:
        chat_files = user_input_raw.files
elif quick_prompt:
    user_text = quick_prompt

if user_text or chat_files:
    # Formulate contextual input
    uploaded_file = st.session_state.get('uploaded_file')
    url_input = st.session_state.get('url_input')
    
    context_text = ""
    images = []
    
    # Files from Sidebar
    if uploaded_file:
        uploaded_file.seek(0)
        content, is_img = process_file_upload(uploaded_file)
        if is_img:
            uploaded_file.seek(0)
            img_obj = load_image(uploaded_file)
            if img_obj: images.append(img_obj)
        elif content:
            context_text += f"\n\n--- Document Context [{uploaded_file.name}] ---\n{content}\n"
            
    # Files from Chat Input
    for cf in chat_files:
        cf.seek(0)
        content, is_img = process_file_upload(cf)
        if is_img:
            cf.seek(0)
            img_obj = load_image(cf)
            if img_obj: images.append(img_obj)
        elif content:
            context_text += f"\n\n--- Document Context [{cf.name}] ---\n{content}\n"
            
    if url_input:
        url_text = fetch_url_text(url_input)
        context_text += f"\n\n--- URL Context [{url_input}] ---\n{url_text}\n"

    final_prompt = user_text + context_text

    msg = {
        "role": "user",
        "content": final_prompt,
        "images": images,
        "file_context": len(context_text) > 0
    }
    
    st.session_state.messages.append(msg)
    
    with st.chat_message("user", avatar="👤"):
        st.markdown(user_text)
        if images:
            cols = st.columns(len(images))
            for i, img in enumerate(images):
                cols[i].image(img, width=200)
    
    eli5_mode = st.session_state.get('eli5_mode', False)
    tone = st.session_state.get('tone_choice', 'Casual')
    model_name = st.session_state.get('model_choice', 'gemini-2.5-flash')
    
    # Intercept Hardik Override
    user_lower = final_prompt.lower()
    hardik_activated = False
    hardik_deactivated = False
    
    if ("hardik" in user_lower and "not" not in user_lower and "who" not in user_lower) and not st.session_state.is_hardik:
        st.session_state.is_hardik = True
        hardik_activated = True
    elif (
        ("not hardik" in user_lower) or 
        ("joking" in user_lower) or 
        ("normal form" in user_lower) or 
        ("deactivate" in user_lower) or 
        ("original form" in user_lower) or 
        ("turn off" in user_lower) or
        (("i am " in user_lower or "im " in user_lower or "i'm " in user_lower) and "hardik" not in user_lower)
    ) and st.session_state.is_hardik:
        st.session_state.is_hardik = False
        hardik_deactivated = True

    if hardik_activated:
        reply = "Welcome sir, glad to serve you! I have initialized the Golden Override protocols."
        st.session_state.messages.append({"role": "assistant", "content": reply})
        st.rerun()
    elif hardik_deactivated:
        reply = "Understood sir. Deactivating Golden Override protocols and reverting to original form."
        st.session_state.messages.append({"role": "assistant", "content": reply})
        st.rerun()

    sys_prompt = get_system_prompt(eli5_mode, tone)
    
    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("Thinking..."):
            try:
                # Dynamic Routing: If images are present, we MUST use Google Gemini. 
                # Otherwise, text queries get rocket-strapped to Llama-3 via Groq!
                has_image = len(st.session_state.messages[-1].get("images", [])) > 0
                
                if has_image or model_name == "gemini-2.5-pro":
                    response = get_response(st.session_state.messages, model_name, sys_prompt)
                else:
                    response = get_groq_response(st.session_state.messages, sys_prompt)
                
                parts = str(response).split("<think>")
                if len(parts) > 1 and "</think>" in parts[1]:
                    think_part = parts[1].split("</think>")[0].strip()
                    answer_part = parts[1].split("</think>")[1].strip()
                    
                    with st.expander("💭 Reasoning..."):
                        st.markdown(think_part)
                    st.markdown(answer_part)
                else:
                    st.markdown(response)
                    
                st.session_state.messages.append({"role": "assistant", "content": response})
            except Exception as e:
                error_msg = str(e)
                if "429" in error_msg or "Quota exceeded" in error_msg:
                    st.error("🚧 The system is currently under maintenance due to high traffic limit. Please come back after 24 hours.")
                else:
                    st.error("An unexpected error occurred while communicating with the AI. Please try again later.")

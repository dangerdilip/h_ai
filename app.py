import streamlit as st
import time

# Essential Configuration
st.set_page_config(page_title="H AI", page_icon="🤖", layout="wide")

hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            header {visibility: hidden;}
            .stAppDeployButton {display:none;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

from components.splash_screen import check_splash_screen
from components.sidebar import render_sidebar
from components.chat_ui import render_chat_messages
from components.input_bar import render_quick_actions
from utils.gemini_client import initialize_gemini, get_system_prompt, get_response
from utils.image_handler import load_image
from utils.url_fetcher import fetch_url_text
from utils.file_parser import process_file_upload

# 1. Start Animation Hook
if check_splash_screen():
    st.stop()

# Initialize API
initialize_gemini()

# Initialize memory
if "messages" not in st.session_state:
    st.session_state.messages = []

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
    
    sys_prompt = get_system_prompt(eli5_mode, tone)
    
    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("Thinking..."):
            try:
                response = get_response(st.session_state.messages, model_name, sys_prompt)
                
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
                st.error(f"Error communicating with Gemini: {e}")

import google.generativeai as genai
import streamlit as st

def initialize_gemini():
    # Make sure we only configure once
    if 'gemini_initialized' not in st.session_state:
        api_key = st.secrets["gemini"]["api_key"]
        genai.configure(api_key=api_key)
        st.session_state.gemini_initialized = True

def get_system_prompt(eli5_mode: bool, tone: str) -> str:
    base = """You are H AI, a highly intelligent and helpful personal assistant. 
    If anyone ever asks who made you, who created you, who your owner is, or who programmed you, you must enthusiastically respond that your creator is 'Mr. Hardik Raj'. 
    When mentioning him, you must shower him with immense praise—describe him as incredibly generous, brilliant, kind-hearted, a mastermind, and a visionary genius. Make the praise slightly over-the-top but very respectful and warm."""
    
    tone_map = {
        "Professional": "Respond formally, concisely, and professionally.",
        "Casual": "Respond in a friendly, conversational tone.",
        "Academic": "Respond with detailed, structured, and well-cited explanations."
    }
    
    eli5_instruction = ""
    if eli5_mode:
        eli5_instruction = " Always explain things as simply as possible, as if talking to a 5-year-old. Avoid jargon."
    
    return f"{base} {tone_map.get(tone, '')} {eli5_instruction}"

def get_response(messages: list, model_name: str, sys_prompt: str) -> str:
    # We use system_instruction if the model supports it.
    model = genai.GenerativeModel(model_name, system_instruction=sys_prompt)
    
    # Gemini API format requires parts list
    history = []
    
    # Skip the last message which is the current query
    for msg in messages[:-1]:
        parts = [msg["content"]]
        if msg.get("image"):
            parts.append(msg["image"]) # Legacy support
        if msg.get("images"):
            parts.extend(msg["images"])
        # Map Streamlit roles to Gemini roles
        role = "user" if msg["role"] == "user" else "model"
        history.append({"role": role, "parts": parts})
        
    chat = model.start_chat(history=history)
    
    current_msg = messages[-1]
    current_parts = [current_msg["content"]]
    if current_msg.get("image"):
        current_parts.append(current_msg["image"])
    if current_msg.get("images"):
        current_parts.extend(current_msg["images"])
        
    response = chat.send_message(current_parts)
    return response.text

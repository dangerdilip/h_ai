import streamlit as st
import os
from groq import Groq

def initialize_groq():
    if 'groq_client' not in st.session_state:
        api_key = st.secrets["groq"]["api_key"]
        st.session_state.groq_client = Groq(api_key=api_key)

def get_groq_response(messages: list, sys_prompt: str) -> str:
    client = st.session_state.groq_client
    
    # Format messages for Groq exactly like the standard Chat completion API
    formatted_messages = []
    
    # Add system prompt as the very first message
    formatted_messages.append({
        "role": "system",
        "content": sys_prompt
    })
    
    # Convert Streamlit history to Groq payload
    for msg in messages:
        # We assume Groq only handles text payload, if images exist they were routed to Gemini
        role = "user" if msg["role"] == "user" else "assistant"
        formatted_messages.append({"role": role, "content": msg["content"]})
        
    chat_completion = client.chat.completions.create(
        messages=formatted_messages,
        model="llama3-70b-8192",
        temperature=0.7,
        max_tokens=4096,
        top_p=1,
        stream=False,
    )
    
    return chat_completion.choices[0].message.content

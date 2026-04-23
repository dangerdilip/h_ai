import streamlit as st

def render_sidebar():
    with st.sidebar:
        st.markdown("### 🟢 H AI System Online")
        st.divider()
        
        # Silently set the engine in the background to hybrid without showing it
        st.session_state.model_choice = "gemini-2.5-flash"
        
        st.session_state.tone_choice = st.radio(
            "Response Style",
            options=["Casual", "Professional", "Academic"]
        )
        
        st.session_state.eli5_mode = st.toggle("🔤 ELI5 Mode", value=False)
        
        st.divider()
        
        # File uploader and URL inside the sidebar keeps the main UI clean
        st.markdown("#### Attachments")
        st.session_state.uploaded_file = st.file_uploader(
            "Upload Image or Document", 
            type=['png', 'jpg', 'jpeg', 'pdf', 'docx', 'csv', 'txt']
        )
        st.session_state.url_input = st.text_input("🔗 Attach URL Context")
        
        st.divider()
        
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
            
        def convert_history():
            if 'messages' not in st.session_state:
                return "No history"
            text = ""
            for msg in st.session_state.messages:
                text += f"[{msg['role'].upper()}]\n{msg['content']}\n\n"
            return text
            
        st.download_button(
            "💾 Export Chat",
            data=convert_history(),
            file_name="h-ai-chat.md",
            mime="text/markdown",
            use_container_width=True
        )

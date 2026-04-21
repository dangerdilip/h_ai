import streamlit as st

def render_chat_messages(messages):
    for msg in messages:
        # User message
        if msg["role"] == "user":
            with st.chat_message("user", avatar="👤"):
                st.markdown(msg["content"])
                if "image" in msg and msg["image"] is not None:
                    # Legacy support
                    st.image(msg["image"], width=200)
                if "images" in msg and msg["images"]:
                    cols = st.columns(len(msg["images"]))
                    for i, img in enumerate(msg["images"]):
                        cols[i].image(img, width=200)
                if "file_context" in msg and msg["file_context"]:
                    with st.expander("📄 Attached Context"):
                        st.text("Context provided from uploaded file/URL.")
        
        # Assistant message
        else:
            with st.chat_message("assistant", avatar="🤖"):
                # Handle chain-of-thought expander if available in our implementation
                parts = str(msg["content"]).split("<think>")
                if len(parts) > 1 and "</think>" in parts[1]:
                    think_part = parts[1].split("</think>")[0].strip()
                    answer_part = parts[1].split("</think>")[1].strip()
                    
                    with st.expander("💭 Reasoning..."):
                        st.markdown(think_part)
                    st.markdown(answer_part)
                else:
                    st.markdown(msg["content"])

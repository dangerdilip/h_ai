import streamlit as st

def render_quick_actions():
    st.markdown("<small>Quick Actions</small>", unsafe_allow_html=True)
    cols = st.columns(5)
    
    actions = {
        "📝 Summarize": "Summarize the context or image I just shared.",
        "🐛 Debug Code": "Find and explain any bugs in this context.",
        "🌍 Translate": "Translate this to English.",
        "📊 Analyse": "Analyse the provided data and give insights.",
        "📖 Explain": "Explain this concept simply."
    }
    
    prompt = None
    for i, (label, action_text) in enumerate(actions.items()):
        with cols[i]:
            if st.button(label, use_container_width=True):
                prompt = action_text
    
    return prompt

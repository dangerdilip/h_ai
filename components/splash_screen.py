import streamlit as st
import streamlit.components.v1 as components
import time
import os

def check_splash_screen():
    # If the splash screen hasn't been shown yet this session
    if 'splash_shown' not in st.session_state:
        st.session_state.splash_shown = False

    if not st.session_state.splash_shown:
        # Show splash screen
        show_splash_screen()
        # Mark as shown
        st.session_state.splash_shown = True
        time.sleep(9.0) # Give it 9 seconds to run the slower animation
        st.rerun() # Refresh to clear it
        return True # It is currently showing
    return False

def show_splash_screen():
    # Create empty container that we'll clear later
    placeholder = st.empty()
    
    html_path = os.path.join(os.path.dirname(__file__), 'animation.html')
    with open(html_path, 'r', encoding='utf-8') as f:
        html_code = f.read()

    with placeholder.container():
        # Remove streamlist margins to allow fullscreen illusion
        st.markdown("<style>.block-container {padding-top: 0rem !important; padding-bottom: 0rem !important; margin: 0 !important; max-width: 100% !important;}</style>", unsafe_allow_html=True)
        # Inject the custom HTML animation, using 600 height so it keeps canvas center perfectly aligned on mobiles
        components.html(html_code, height=600)
    
    return placeholder

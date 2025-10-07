# Recommender/auth.py
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
import streamlit as st

def get_spotify_client():
    """Authenticate and return a Spotify client for Streamlit Cloud."""
    
    st.write("🔄 Starting authentication process...")
    
    # Use Streamlit secrets (for cloud) or environment variables (for local)
    client_id = st.secrets.get("SPOTIPY_CLIENT_ID", os.environ.get("SPOTIPY_CLIENT_ID"))
    client_secret = st.secrets.get("SPOTIPY_CLIENT_SECRET", os.environ.get("SPOTIPY_CLIENT_SECRET"))
    redirect_uri = st.secrets.get("SPOTIPY_REDIRECT_URI", os.environ.get("SPOTIPY_REDIRECT_URI"))
    
    st.write(f"Client ID: {client_id[:10]}..." if client_id else "Client ID: Not found")
    st.write(f"Client Secret: {'Found' if client_secret else 'Not found'}")
    
    if not client_id or not client_secret:
        st.error("""
        ❌ Spotify credentials not found!
        
        Please set them in Streamlit Cloud secrets:
        1. Click '⋮' → Settings → Secrets
        2. Add:
           SPOTIPY_CLIENT_ID = "your_client_id"
           SPOTIPY_CLIENT_SECRET = "your_client_secret" 
           SPOTIPY_REDIRECT_URI = "https://recommender-app-czrbvi2mrvmz2ggez8ove9.streamlit.app"
        """)
        st.stop()
    
    # Clear any existing cache
    if os.path.exists(".cache"):
        os.remove(".cache")
        st.write("🗑️ Cleared existing cache")
    
    try:
        auth_manager = SpotifyOAuth(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=redirect_uri,
            scope="user-library-read",
            cache_path=".cache",
            show_dialog=True
        )
        
        # Get authorization URL to create login button
        auth_url = auth_manager.get_authorize_url()
        
        st.write("---")
        st.write("## 🔑 Login Required")
        st.write("Click the button below to authenticate with Spotify:")
        
        # Create login button
        if st.button("🎵 Login with Spotify", type="primary", use_container_width=True):
            # This will redirect to Spotify
            st.markdown(f'<meta http-equiv="refresh" content="0; url={auth_url}">', unsafe_allow_html=True)
            st.info("Redirecting to Spotify...")
            st.stop()
        
        st.write("---")
        
        # Try to authenticate (will work after user authorizes)
        sp = spotipy.Spotify(auth_manager=auth_manager)
        user = sp.current_user()
        st.success(f"✅ Authenticated as: {user.get('display_name', 'User')}")
        return sp
        
    except Exception as e:
        st.error(f"❌ Authentication failed: {e}")
        st.info("Please click the 'Login with Spotify' button above to authorize the app.")
        return None

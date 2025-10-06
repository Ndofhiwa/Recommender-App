# Recommender/auth.py
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
import streamlit as st
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def get_spotify_client():
    """Authenticate and return a Spotify client."""
    
    st.write("🔄 Starting authentication process...")
    
    # Load credentials
    client_id = os.environ.get("SPOTIPY_CLIENT_ID")
    client_secret = os.environ.get("SPOTIPY_CLIENT_SECRET")
    
    st.write(f"Client ID: {client_id[:10]}..." if client_id else "Client ID: Not found")
    st.write(f"Client Secret: {'Found' if client_secret else 'Not found'}")
    
    if not client_id or not client_secret:
        st.error("❌ Spotify credentials not found!")
        st.stop()
    
    # Clear any existing cache
    if os.path.exists(".cache"):
        os.remove(".cache")
        st.write("🗑️ Cleared existing cache")
    
    try:
        # Use HTTPS for local development
        redirect_uri = "https://localhost:8501"
        
        auth_manager = SpotifyOAuth(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=redirect_uri,
            scope="user-library-read",
            cache_path=".cache",
            show_dialog=True
        )
        
        sp = spotipy.Spotify(auth_manager=auth_manager)
        
        # Test authentication with a simple call
        user = sp.current_user()
        st.success(f"✅ Authenticated as: {user.get('display_name', 'User')}")
        
        return sp
        
    except Exception as e:
        st.error(f"❌ Authentication failed: {e}")
        st.info("""
        **For local development with HTTPS:**
        
        Option 1: Use a different redirect URI that Spotify accepts:
        - https://oauth.pstgr.io/ (free service)
        - Or deploy to Streamlit Cloud and use that URL
        
        Option 2: Use HTTP but with a different port that might work:
        - http://localhost:8080
        - http://localhost:8888
        
        Option 3: Use a tunneling service:
        - ngrok (creates HTTPS tunnel to your localhost)
        - localhost.run
        """)
        st.stop()
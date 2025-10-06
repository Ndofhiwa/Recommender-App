import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
import streamlit as st

def get_spotify_client():
    """Authenticate and return a Spotify client."""
    
    # For Streamlit, use localhost redirect
    redirect_uri = "http://localhost:8501"
    
    scope = "user-library-read"
    
    client_id = os.environ.get("SPOTIPY_CLIENT_ID")
    client_secret = os.environ.get("SPOTIPY_CLIENT_SECRET")
    
    if not client_id or not client_secret:
        st.error("""
        ❌ Spotify credentials not found!
        
        Please set these environment variables:
        - SPOTIPY_CLIENT_ID
        - SPOTIPY_CLIENT_SECRET
        
        You can set them in Streamlit Cloud secrets or in a .env file.
        """)
        st.stop()
    
    try:
        auth_manager = SpotifyOAuth(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=redirect_uri,
            scope=scope,
            cache_path=".cache",
            show_dialog=True
        )
        
        sp = spotipy.Spotify(auth_manager=auth_manager)
        
        # Test authentication
        user = sp.current_user()
        st.success(f"✅ Authenticated as: {user.get('display_name', 'User')}")
        return sp
        
    except Exception as e:
        st.error(f"❌ Authentication failed: {e}")
        st.info("""
        **Troubleshooting steps:**
        1. Make sure your Spotify app has the correct redirect URI: http://localhost:8501
        2. Check that your credentials are correct
        3. Try clearing the cache by deleting the `.cache` file
        """)
        st.stop()
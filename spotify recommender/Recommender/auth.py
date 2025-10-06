import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
from dotenv import load_dotenv
import streamlit as st

# Load environment variables
load_dotenv()

def get_spotify_client():
    """Authenticate and return a Spotify client with better error handling."""
    
    # Required scopes
    scope = "user-library-read user-read-recently-played user-top-read"
    
    # Get credentials from environment
    client_id = os.getenv("SPOTIPY_CLIENT_ID")
    client_secret = os.getenv("SPOTIPY_CLIENT_SECRET")
    redirect_uri = os.getenv("SPOTIPY_REDIRECT_URI")
    
    # Validate credentials
    if not client_id or not client_secret:
        st.error("Missing Spotify credentials. Please check your .env file.")
        st.stop()
    
    try:
        auth_manager = SpotifyOAuth(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=redirect_uri,
            scope=scope,
            cache_path=".cache",
            show_dialog=True  # Force re-authentication if needed
        )
        
        # Get access token
        token_info = auth_manager.get_access_token()
        
        if not token_info:
            st.error("Could not get access token. Please check your credentials.")
            st.stop()
        
        # Create Spotify client
        sp = spotipy.Spotify(auth=token_info['access_token'])
        
        # Test authentication
        user = sp.current_user()
        st.success(f"✅ Authenticated as: {user.get('display_name', 'User')}")
        
        return sp
        
    except Exception as e:
        st.error(f"Spotify authentication error: {str(e)}")
        st.info("Please check your credentials and try again.")
        st.stop()
# Recommender/auth.py
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
import streamlit as st

def get_spotify_client():
    """Authenticate and return a Spotify client for Streamlit Cloud."""
    
    st.write("🔄 Starting authentication process...")
    
    # Use Streamlit secrets
    client_id = st.secrets.get("SPOTIPY_CLIENT_ID")
    client_secret = st.secrets.get("SPOTIPY_CLIENT_SECRET") 
    redirect_uri = st.secrets.get("SPOTIPY_REDIRECT_URI")
    
    st.write(f"Client ID: {client_id[:10]}..." if client_id else "Client ID: Not found")
    st.write(f"Client Secret: {'Found' if client_secret else 'Not found'}")
    st.write(f"Redirect URI: {redirect_uri}")
    
    if not client_id or not client_secret or not redirect_uri:
        st.error("❌ Spotify credentials not found in secrets!")
        st.stop()
    
    try:
        auth_manager = SpotifyOAuth(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=redirect_uri,
            scope="user-library-read",
            cache_path=".cache",
            show_dialog=True
        )
        
        # Check if we already have a token
        token_info = auth_manager.get_cached_token()
        
        if token_info and not auth_manager.is_token_expired(token_info):
            # We're already authenticated
            sp = spotipy.Spotify(auth_manager=auth_manager)
            user = sp.current_user()
            st.success(f"✅ Authenticated as: {user.get('display_name', 'User')}")
            return sp
        
        # SHOW LOGIN BUTTON - We need authentication
        st.write("---")
        st.write("## 🔑 Spotify Login Required")
        st.write("### Click the link below to authenticate:")
        
        # Create the login link that opens in new tab
        auth_url = auth_manager.get_authorize_url()
        st.markdown(f'<a href="{auth_url}" target="_blank"><button style="background-color: #1DB954; color: white; padding: 15px 30px; border: none; border-radius: 25px; font-size: 18px; cursor: pointer;">🎵 LOGIN WITH SPOTIFY</button></a>', unsafe_allow_html=True)
        
        st.write("---")
        st.info("💡 **After clicking the button, a new tab will open for Spotify login. Complete the authentication there, then return to this tab and REFRESH THE PAGE.**")
        
        # Try to get the token from the callback URL
        try:
            # This will handle the callback and get the token
            sp = spotipy.Spotify(auth_manager=auth_manager)
            user = sp.current_user()
            st.success(f"✅ Authenticated as: {user.get('display_name', 'User')}")
            return sp
        except:
            st.warning("🔐 **Waiting for authentication... Please complete the Spotify login and refresh this page.**")
            return None
        
    except Exception as e:
        st.error(f"❌ Authentication error: {str(e)}")
        st.info("💡 **Please complete the Spotify login and refresh this page.**")
        return None

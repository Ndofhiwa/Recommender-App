# Recommender/auth.py
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
import streamlit as st

def get_spotify_client():
    """Safe authentication with both text URL and optional button."""
    
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
        
        # SAFE AUTHENTICATION OPTIONS
        st.write("---")
        st.write("## 🔑 Spotify Login Required")
        
        # Show the safe text URL (primary method)
        st.write("### 🔒 Safe Method (Recommended):")
        auth_url = f"https://accounts.spotify.com/authorize?client_id={client_id}&response_type=code&redirect_uri={redirect_uri}&scope=user-library-read"
        
        st.text_area("Copy this URL:", auth_url, height=80, key="auth_url")
        
        st.write("**Steps:**")
        st.write("1. **Copy the URL above**")
        st.write("2. **Paste into a new browser tab**")
        st.write("3. **Log in with Spotify**")
        st.write("4. **Authorize the app**")
        st.write("5. **Return here and refresh**")
        
        # Optional button method (with security warning)
        st.write("### ⚡ Quick Method (Use with caution):")
        st.markdown(f'<a href="{auth_url}" target="_blank"><button style="background-color: #1DB954; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer;">🎵 Login with Spotify</button></a>', unsafe_allow_html=True)
        
        st.write("---")
        st.warning("🚨 **SECURITY ALERT:** If you're asked to download anything, close the tab immediately and use the Safe Method above!")
        st.info("💡 **After completing authentication in either method, return here and REFRESH THIS PAGE.**")
        
        # Try to get the token from the callback URL
        try:
            # This will handle the callback and get the token
            sp = spotipy.Spotify(auth_manager=auth_manager)
            user = sp.current_user()
            st.success(f"✅ Authenticated as: {user.get('display_name', 'User')}")
            return sp
        except:
            st.warning("🔐 **Waiting for authentication... Please complete Spotify login and refresh this page.**")
            return None
        
    except Exception as e:
        st.error(f"❌ Authentication error: {str(e)}")
        st.info("💡 **Please complete the Spotify login using one of the methods above and refresh this page.**")
        return None

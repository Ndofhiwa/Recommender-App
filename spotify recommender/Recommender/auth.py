# Recommender/auth.py
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
import streamlit as st

def get_spotify_client():
    """Manual authentication flow to avoid redirect loops."""
    
    st.write("🔄 Starting authentication process...")
    
    # Use Streamlit secrets
    client_id = st.secrets.get("SPOTIPY_CLIENT_ID")
    client_secret = st.secrets.get("SPOTIPY_CLIENT_SECRET") 
    redirect_uri = st.secrets.get("SPOTIPY_REDIRECT_URI")
    
    st.write(f"Client ID: {client_id[:10]}...")
    st.write(f"Client Secret: Found")
    st.write(f"Redirect URI: {redirect_uri}")
    
    if not client_id or not client_secret or not redirect_uri:
        st.error("❌ Spotify credentials not found!")
        st.stop()
    
    try:
        # Clear any cached tokens
        if os.path.exists(".cache"):
            os.remove(".cache")
            st.write("🗑️ Cleared previous authentication cache")
        
        auth_manager = SpotifyOAuth(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=redirect_uri,
            scope="user-library-read",
            cache_path=".cache",
            show_dialog=True
        )
        
        # Check if we're in a callback (has URL parameters) - USING NEW METHOD
        query_params = st.query_params  # NEW: Fixed deprecated method
        
        if 'code' in query_params:
            # We're in the callback - try to get the token
            try:
                st.write("🔄 Processing callback...")
                sp = spotipy.Spotify(auth_manager=auth_manager)
                user = sp.current_user()
                st.success(f"✅ Authenticated as: {user.get('display_name', 'User')}")
                # Clear the URL parameters
                st.query_params.clear()  # NEW: Fixed deprecated method
                return sp
            except Exception as e:
                st.error(f"❌ Callback processing failed: {e}")
        
        # Check if we already have a valid token
        token_info = auth_manager.get_cached_token()
        if token_info and not auth_manager.is_token_expired(token_info):
            sp = spotipy.Spotify(auth_manager=auth_manager)
            user = sp.current_user()
            st.success(f"✅ Authenticated as: {user.get('display_name', 'User')}")
            return sp
        
        # MANUAL AUTHENTICATION FLOW
        st.write("---")
        st.write("## 🔑 Manual Authentication Required")
        st.write("### Due to browser security, we need to manually handle authentication.")
        
        # Generate the authorization URL
        auth_url = auth_manager.get_authorize_url()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("### Method 1: Copy URL")
            st.text_area("Copy this URL:", auth_url, height=60)
            st.write("1. Copy the URL above")
            st.write("2. Open a new tab")
            st.write("3. Paste and go")
            st.write("4. Log in with Spotify")
            st.write("5. You'll be redirected back here")
        
        with col2:
            st.write("### Method 2: Direct Link")
            st.markdown(f'<a href="{auth_url}" target="_blank" style="text-decoration: none;"><button style="background-color: #1DB954; color: white; padding: 12px 24px; border: none; border-radius: 25px; font-size: 16px; cursor: pointer; width: 100%;">🎵 Open Spotify Login</button></a>', unsafe_allow_html=True)
            st.write("1. Click the button")
            st.write("2. Log in with Spotify") 
            st.write("3. Authorize the app")
            st.write("4. You'll return here automatically")
        
        st.write("---")
        st.info("💡 **After authorizing, you'll be redirected back here. If it shows the login page again, just wait a moment and refresh.**")
        
        # Return None to indicate we need authentication
        return None
        
    except Exception as e:
        st.error(f"❌ Authentication error: {str(e)}")
        return None

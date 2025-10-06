# debug_test.py - Run this instead of main.py for now
import streamlit as st
import traceback
import sys

st.set_page_config(page_title="Spotify Debug", layout="wide")
st.title("🎵 Spotify App - Debug Test")

st.write("### 🔧 Let's find where it breaks...")

try:
    # Test 1: Basic imports
    st.write("#### 1. Testing imports...")
    try:
        from Recommender.auth import get_spotify_client
        from Recommender.data import get_user_saved_songs, get_audio_features
        st.success("✅ All imports work!")
    except ImportError as e:
        st.error(f"❌ Import failed: {e}")
        st.stop()

    # Test 2: Authentication
    st.write("#### 2. Testing authentication...")
    try:
        sp = get_spotify_client()
        st.success("✅ Authentication successful!")
    except Exception as e:
        st.error(f"❌ Auth failed: {e}")
        st.stop()

    # Test 3: Get saved songs
    st.write("#### 3. Testing saved songs...")
    try:
        saved_songs = get_user_saved_songs(sp, limit=3)
        st.write(f"✅ Found {len(saved_songs)} songs")
        if not saved_songs.empty:
            st.dataframe(saved_songs)
        else:
            st.error("❌ No saved songs found!")
            st.stop()
    except Exception as e:
        st.error(f"❌ Saved songs failed: {e}")
        st.stop()

    # Test 4: Audio features
    st.write("#### 4. Testing audio features...")
    try:
        track_uris = saved_songs['uri'].tolist()
        st.write(f"Processing URIs: {track_uris[:2]}...")
        
        audio_data = get_audio_features(sp, track_uris)
        st.write(f"✅ Got {len(audio_data)} audio features")
        
        if not audio_data.empty:
            st.dataframe(audio_data.head(2))
            
            # Test 5: Simple merge
            st.write("#### 5. Testing data merge...")
            combined_data = saved_songs.merge(audio_data, on='uri', how='left')
            st.write(f"✅ Merged data: {len(combined_data)} rows")
            st.success("🎉 All tests passed! Your basic app structure works!")
        else:
            st.error("❌ No audio features data")
            
    except Exception as e:
        st.error(f"❌ Audio features failed: {e}")
        st.code(traceback.format_exc())

except Exception as e:
    st.error(f"💥 Major error: {e}")
    st.code(traceback.format_exc())
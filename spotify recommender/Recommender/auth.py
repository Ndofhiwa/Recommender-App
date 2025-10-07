import streamlit as st
from Recommender.auth import get_spotify_client
from Recommender.data import get_user_saved_songs, get_audio_features
from Recommender.recommend import recommend_from_song

# App setup
st.set_page_config(page_title="Spotify Recommender", layout="wide")
st.title("🎵 Spotify Song Recommender")

try:
    # Step 1: Authentication
    st.write("### Step 1: Authentication")
    sp = get_spotify_client()
    
    if sp is None:
        st.info("Please complete the Spotify authentication above to continue.")
        st.stop()
    
    # Step 2: Get saved songs
    st.write("### Step 2: Loading your saved songs...")
    saved_songs = get_user_saved_songs(sp, limit=20)
    
    if saved_songs.empty:
        st.error("No saved songs found. Please save some songs in Spotify first.")
        st.stop()
    
    # Show what songs we found
    st.write("#### Your Saved Songs:")
    st.dataframe(saved_songs[['artist', 'track']])
    
    # Rest of your existing code...
    st.write("### Step 3: Analyzing audio features...")
    track_uris = saved_songs['uri'].tolist()
    audio_data = get_audio_features(sp, track_uris)
    
    if audio_data.empty:
        st.error("Could not fetch audio features. Please try again.")
        st.stop()
    
    # Merge data
    songs_with_audio = saved_songs.merge(audio_data, on='uri', how='left')
    st.success(f"✅ Combined {len(songs_with_audio)} songs with audio features")
    
    # Recommendations
    st.write("### Step 4: Get Recommendations")
    valid_songs = songs_with_audio.dropna(subset=['danceability'])
    
    if valid_songs.empty:
        st.error("No songs with complete audio features available.")
        st.stop()
    
    song_options = [f"{row['track']} by {row['artist']}" for _, row in valid_songs.iterrows()]
    selected_display = st.selectbox("Choose a song from your library:", song_options)
    
    if st.button("Find Similar Songs"):
        with st.spinner("Finding similar songs..."):
            recommendations = recommend_from_song(selected_display, songs_with_audio, top_n=5)
            
            if recommendations.empty:
                st.warning("No recommendations found. Try selecting a different song.")
            else:
                st.write("#### 🎧 Recommended Songs:")
                for idx, row in recommendations.iterrows():
                    st.write(f"**{row['track']}** by {row['artist']}")
                    st.write(f"🔗 [Listen on Spotify]({row['spotify_link']})")
                    st.write("---")

except Exception as e:
    st.error(f"Application error: {str(e)}")

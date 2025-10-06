import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.metrics.pairwise import cosine_similarity

FEATURE_COLS = [
    'danceability', 'energy', 'key', 'loudness', 'mode', 
    'speechiness', 'acousticness', 'instrumentalness', 'liveness', 
    'valence', 'tempo'
]

def recommend_from_song(selected_song_display: str, songs_with_audio: pd.DataFrame, top_n: int = 5) -> pd.DataFrame:
    """
    Recommend similar songs based on audio features
    """
    try:
        # Filter out songs without audio features
        valid_songs = songs_with_audio.dropna(subset=['danceability']).copy()
        
        if valid_songs.empty:
            st.write("❌ No valid songs with audio features")
            return pd.DataFrame()
        
        # Extract track name from the display string (format: "Track by Artist")
        selected_track = selected_song_display.split(" by ")[0].strip()
        
        # Find the selected song (more flexible matching)
        selected_song_data = valid_songs[
            valid_songs['track'].str.lower().str.contains(selected_track.lower(), na=False)
        ]
        
        if selected_song_data.empty:
            st.write(f"❌ Could not find '{selected_track}' in the data")
            st.write(f"Available tracks: {valid_songs['track'].tolist()}")
            return pd.DataFrame()
        
        # Reset index for reliable indexing
        valid_songs = valid_songs.reset_index(drop=True)
        selected_idx = selected_song_data.index[0]
        
        # Ensure all required feature columns exist
        for col in FEATURE_COLS:
            if col not in valid_songs.columns:
                valid_songs[col] = 0.0

        # Fill any remaining NaN values
        valid_songs[FEATURE_COLS] = valid_songs[FEATURE_COLS].fillna(0.0)
        
        # Standardize the features
        scaler = StandardScaler()
        scaled_features = scaler.fit_transform(valid_songs[FEATURE_COLS])
        
        # Calculate cosine similarity
        similarity_matrix = cosine_similarity(scaled_features)
        
        # Get similarity scores for the selected song
        similarity_scores = list(enumerate(similarity_matrix[selected_idx]))
        
        # Sort by similarity (highest first)
        similarity_scores = sorted(similarity_scores, key=lambda x: x[1], reverse=True)
        
        # Get top N recommendations (excluding the song itself)
        top_recommendations = []
        for idx, score in similarity_scores[1:top_n+1]:  # Skip first (itself)
            song_data = valid_songs.iloc[idx]
            
            # Create Spotify link
            spotify_link = song_data.get('spotify_link')
            if pd.isna(spotify_link) or not spotify_link:
                uri = song_data.get('uri', '')
                if uri and 'spotify:track:' in uri:
                    track_id = uri.split(':')[-1]
                    spotify_link = f"https://open.spotify.com/track/{track_id}"
                else:
                    track_id = song_data.get('id', '')
                    if track_id:
                        spotify_link = f"https://open.spotify.com/track/{track_id}"
                    else:
                        spotify_link = "#"
            
            top_recommendations.append({
                'track': song_data['track'],
                'artist': song_data['artist'],
                'spotify_link': spotify_link,
                'similarity_score': score,
                'danceability': song_data.get('danceability'),
                'energy': song_data.get('energy'),
                'valence': song_data.get('valence')
            })
        
        return pd.DataFrame(top_recommendations)
        
    except Exception as e:
        st.error(f"Error in recommendation: {e}")
        import traceback
        st.write(f"Detailed error: {traceback.format_exc()}")
        return pd.DataFrame()
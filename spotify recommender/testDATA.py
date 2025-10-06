from Recommender.data import get_user_saved_songs, get_audio_features
from Recommender.auth import get_spotify_client

sp = get_spotify_client()

# Step 1: Get saved songs
saved_songs = get_user_saved_songs(sp, limit=30)

# Step 2: Get audio features + metadata in one DataFrame
audio_data = get_audio_features(sp, saved_songs)

print(audio_data.head())

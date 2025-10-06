# Recommender/recommend.py

import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.metrics.pairwise import cosine_similarity
from .features import FEATURE_COLS  # ✅ relative import

def recommend_from_song(song_name: str, audio_df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    """Recommend songs similar to the given song using Spotify audio features."""
    if audio_df.empty:
        return pd.DataFrame()

    # Ensure all required feature columns exist
    for col in FEATURE_COLS:
        if col not in audio_df.columns:
            audio_df[col] = 0.0

    audio_df[FEATURE_COLS] = audio_df[FEATURE_COLS].fillna(0.0)

    scaler = StandardScaler()
    features_scaled = scaler.fit_transform(audio_df[FEATURE_COLS])
    sim_matrix = cosine_similarity(features_scaled)

    matches = audio_df[audio_df["track"].str.lower() == song_name.lower()]
    if matches.empty:
        return pd.DataFrame()

    idx = matches.index[0]
    similarity_scores = sorted(
        list(enumerate(sim_matrix[idx])),
        key=lambda x: x[1],
        reverse=True
    )[1: top_n + 1]

    recommendations = audio_df.iloc[[i[0] for i in similarity_scores]][
        ["artist", "track", "id", "uri"]
    ].copy()

    recommendations["spotify_link"] = recommendations["uri"].apply(
        lambda x: f"https://open.spotify.com/track/{x.split(':')[-1]}"
    )

    return recommendations.reset_index(drop=True)




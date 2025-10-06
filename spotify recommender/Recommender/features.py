

FEATURE_COLS = [
    "danceability",
    "energy",
    "key",
    "loudness",
    "mode",
    "speechiness",
    "acousticness",
    "instrumentalness",
    "liveness",
    "valence",
    "tempo",
    "duration_ms",
]

def get_feature_columns():
    """Return the list of Spotify audio feature columns."""
    return FEATURE_COLS


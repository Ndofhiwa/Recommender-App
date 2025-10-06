import pandas as pd
import time
import requests
from spotipy.exceptions import SpotifyException
from .features import FEATURE_COLS  # ✅ use FEATURE_COLS here


def get_user_saved_songs(sp, limit=30):
    """Fetch user's saved songs (returns IDs + URIs + metadata)."""
    tracks = []
    offset = 0
    fetched = 0
    per_request = 50  # Spotify max per request

    while fetched < limit:
        batch = sp.current_user_saved_tracks(limit=per_request, offset=offset)
        items = batch.get("items", [])

        if not items:
            break

        for item in items:
            track = item.get("track")
            if not track:
                continue

            uri = track.get("uri", "")
            track_id = track.get("id", "")

            if track_id:
                tracks.append({
                    "id": track_id,
                    "uri": uri,
                    "track": track["name"],
                    "artist": track["artists"][0]["name"],
                    "spotify_link": track["external_urls"]["spotify"],
                })

        fetched += len(items)
        offset += len(items)

        if not batch.get("next"):
            break

    return pd.DataFrame(tracks)


def get_audio_features(sp, uris, chunk_size=30, max_retries=1, retry_delay=3):
    """Fetch audio features for a list of track URIs from Spotify."""
    rows = []

    for i in range(0, len(uris), chunk_size):
        chunk = uris[i:i + chunk_size]
        retries = 0

        while retries <= max_retries:
            try:
                features = sp.audio_features(chunk)

                for j, feat in enumerate(features):
                    # Always create a row with FEATURE_COLS, even if feat is None
                    row = {col: (feat.get(col) if feat else None) for col in FEATURE_COLS} # pyright: ignore[reportGeneralTypeIssues]

                    # Track metadata
                    try:
                        track_info = sp.track(chunk[j])
                        row["track"] = track_info.get("name", None)
                        row["artist"] = track_info["artists"][0]["name"] if track_info.get("artists") else None
                        row["id"] = track_info.get("id", None)
                        row["uri"] = chunk[j]
                        row["spotify_link"] = track_info["external_urls"]["spotify"]
                    except Exception:
                        # If metadata fails, still keep the row
                        row.update({
                            "track": None,
                            "artist": None,
                            "id": None,
                            "uri": chunk[j],
                            "spotify_link": None,
                        })

                    rows.append(row)

                break  # ✅ success → exit retry loop

            except (SpotifyException, requests.exceptions.ReadTimeout) as e:
                retries += 1
                if retries > max_retries:
                    print(f"⚠️ Skipping chunk {chunk} after {max_retries} retries. Error: {e}")
                else:
                    print(f"⏳ Retry {retries}/{max_retries} for chunk {chunk} after error: {e}")
                    time.sleep(retry_delay)

    df = pd.DataFrame(rows)

    # Ensure all FEATURE_COLS exist, even if missing
    for col in FEATURE_COLS: # pyright: ignore[reportGeneralTypeIssues]
        if col not in df.columns:
            df[col] = None

    return df










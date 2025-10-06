import pandas as pd
import streamlit as st
import time

def get_user_saved_songs(sp, limit=30):
    """Fetch user's saved songs."""
    try:
        results = sp.current_user_saved_tracks(limit=limit)
        tracks = []
        
        for item in results['items']:
            track = item['track']
            tracks.append({
                'id': track['id'],
                'uri': track['uri'],
                'track': track['name'],
                'artist': track['artists'][0]['name'],
                'spotify_link': track['external_urls']['spotify']
            })
        
        st.success(f"✅ Found {len(tracks)} saved songs")
        return pd.DataFrame(tracks)
    
    except Exception as e:
        st.error(f"Error fetching saved songs: {e}")
        return pd.DataFrame()

def get_audio_features(sp, track_uris_or_ids):
    """Get audio features for track URIs or IDs"""
    st.write("🔍 Starting audio features analysis...")
    
    if not track_uris_or_ids:
        st.error("No track URIs/IDs provided")
        return pd.DataFrame()
    
    st.write(f"📊 Processing {len(track_uris_or_ids)} tracks...")
    
    # Extract track IDs (handle both URIs and raw IDs)
    track_ids = []
    for item in track_uris_or_ids:
        if item and isinstance(item, str):
            if 'spotify:track:' in item:
                # It's a URI, extract the ID
                track_id = item.split(':')[-1]
                track_ids.append(track_id)
            elif len(item) == 22:
                # It's already a track ID
                track_ids.append(item)
            else:
                st.write(f"   ❌ Invalid format: {item}")
        else:
            st.write(f"   ❌ Invalid item: {item}")
    
    st.write(f"📊 Extracted {len(track_ids)} valid track IDs")
    st.write(f"Sample track IDs: {track_ids[:3]}")
    
    if not track_ids:
        st.error("No valid track IDs could be extracted")
        return pd.DataFrame()
    
    all_features = []
    
    # Process in smaller batches for debugging
    batch_size = 10  # Smaller batch size for debugging
    total_batches = (len(track_ids) + batch_size - 1) // batch_size
    
    for i in range(0, len(track_ids), batch_size):
        batch_ids = track_ids[i:i + batch_size]
        batch_num = (i // batch_size) + 1
        
        st.write(f"   🔄 Processing batch {batch_num}/{total_batches} ({len(batch_ids)} tracks)...")
        
        try:
            # Get audio features for this batch
            st.write(f"   📡 Calling sp.audio_features() with {len(batch_ids)} track IDs...")
            features = sp.audio_features(batch_ids)
            
            if features is None:
                st.error("   ❌ sp.audio_features() returned None")
                continue
                
            st.write(f"   📨 API returned {len(features)} items")
            
            if features:
                valid_count = sum(1 for f in features if f is not None)
                none_count = sum(1 for f in features if f is None)
                st.write(f"   📊 Valid features: {valid_count}, None results: {none_count}")
                
                if valid_count > 0:
                    valid_features = [f for f in features if f is not None]
                    all_features.extend(valid_features)
                    st.write(f"   ✅ Added {len(valid_features)} features to results")
                    
                    # Show sample of what we got
                    if len(valid_features) > 0:
                        sample_feature = valid_features[0]
                        st.write(f"   🔍 Sample feature keys: {list(sample_feature.keys())}")
                else:
                    st.write(f"   ⚠️ No valid features in this batch")
                    st.write(f"   💡 Batch IDs that failed: {batch_ids}")
            else:
                st.write(f"   ❌ features list is empty")
            
            # Small delay
            time.sleep(0.5)
            
        except Exception as e:
            st.error(f"   💥 Exception in batch {batch_num}: {str(e)}")
            st.error(f"   💥 Exception type: {type(e).__name__}")
            continue
    
    st.write(f"📈 Finished processing. Total features collected: {len(all_features)}")
    
    if not all_features:
        st.error("❌ No audio features collected in any batch")
        st.error("💡 Possible issues:")
        st.error("   - Track IDs might not exist in Spotify's database")
        st.error("   - API rate limiting")
        st.error("   - Authentication issues")
        return pd.DataFrame()
    
    # Convert to DataFrame
    try:
        df = pd.DataFrame(all_features)
        st.write(f"💾 DataFrame created with shape: {df.shape}")
        
        if df.empty:
            st.error("❌ DataFrame is empty after conversion")
            return pd.DataFrame()
        
        # Check if we have the essential columns
        st.write(f"💾 DataFrame columns: {df.columns.tolist()}")
        
        # Ensure we have URI column
        if 'uri' not in df.columns and 'id' in df.columns:
            df['uri'] = 'spotify:track:' + df['id']
            st.write("💾 Added missing 'uri' column from IDs")
        
        # Select relevant audio feature columns
        audio_feature_cols = [
            'id', 'uri', 'danceability', 'energy', 'key', 'loudness', 
            'mode', 'speechiness', 'acousticness', 'instrumentalness', 
            'liveness', 'valence', 'tempo', 'duration_ms', 'time_signature'
        ]
        
        available_cols = [col for col in audio_feature_cols if col in df.columns]
        st.write(f"💾 Using columns: {available_cols}")
        
        if not available_cols:
            st.error("❌ No audio feature columns available")
            return pd.DataFrame()
            
        df = df[available_cols]
        
        st.success(f"🎉 Success! Analyzed {len(df)} tracks")
        return df
        
    except Exception as e:
        st.error(f"❌ Error converting to DataFrame: {str(e)}")
        return pd.DataFrame()
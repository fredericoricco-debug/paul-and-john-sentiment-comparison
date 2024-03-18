import json
import pandas as pd
from nltk.metrics import jaccard_distance
from nltk.util import ngrams
import unidecode
from tqdm import tqdm
import time

# get the lyric fetcher
from genius_api import GeniusSearch, get_lyrics

# Normalize text function
def normalize_text(text):
    text = unidecode.unidecode(text)  # Normalize UTF-8 characters to ASCII
    text = text.lower()  # Convert to lowercase
    return text

# Calculate similarity score between two texts
def calculate_similarity(text1, text2, n=2):
    # Normalize texts
    text1 = normalize_text(text1)
    text2 = normalize_text(text2)
    
    # Create n-grams
    grams1 = set(ngrams(text1, n))
    grams2 = set(ngrams(text2, n))
    
    # Calculate Jaccard distance and subtract from 1 to get similarity
    similarity = 1 - jaccard_distance(grams1, grams2)
    return similarity

# Matching songs and adding IDs
def match_songs_and_add_ids(df, songs_json):
    song_id_list = []
    for csv_song_name in tqdm(df['Song']):
        highest_similarity = 0
        closest_song_id = None
        for song_id, song_info in songs_json.items():
            json_song_name = song_info['song_name']
            similarity = calculate_similarity(csv_song_name, json_song_name)
            if similarity > highest_similarity:
                highest_similarity = similarity
                closest_song_id = song_id
        song_id_list.append(closest_song_id)
    df['Song ID'] = song_id_list
    return df

def add_lyrics_to_df(df, songs_json, genius=GeniusSearch()):
    lyrics_list = []
    for song_id in tqdm(df['Song ID']):
        lyrics = get_lyrics(song_id, genius)
        time.sleep(0.5)
        lyrics_list.append(lyrics)
    df['Lyrics'] = lyrics_list
    return df

if __name__ == "__main__":
    # Load the data
    df = pd.read_csv("beatles_songs.csv")
    # Read the beatles songs data
    with open("artist_data/the_beatles_songs.json", "r") as file:
        beatles_songs = json.load(file)

    # Drop the "Singer" column from the dataframe
    df = df.drop("Singer", axis=1)

    # Drop all rows where Composer is neither "Lennon" or "McCartney"
    df = df[df["Composer"].isin(["Lennon", "McCartney"])]

    # Match the songs and add the IDs
    df_updated = match_songs_and_add_ids(df, beatles_songs)

    # Get the lyrics for the songs
    df_updated = add_lyrics_to_df(df_updated, beatles_songs)

    # Save the updated dataframe
    df_updated.to_csv("beatles_songs_with_ids.csv", index=False)
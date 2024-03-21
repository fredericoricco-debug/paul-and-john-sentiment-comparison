# General import
from tqdm import tqdm
import os
import json
import re
import pandas as pd

# My classes
from data_gathering_helpers.genius_api import GeniusSearch, get_lyrics
from data_gathering_helpers.beatles_specific import process_beatles_data

def normalize_song_name(song_name):
    """Normalize the song name by removing common version descriptors."""
    pattern = re.compile(r'\(.*?\)|\[.*?\]|{.*?}| - .*|$')
    return pattern.sub('', song_name).strip().lower()

def confirm_with_user(list, limit, file_path, initial_page, final_message = None):
    print("The following artists will be queried for lyrics:")
    for artist in list:
        print(artist)
    proceed = input("Do you want to proceed? (y/n): ")
    if proceed.lower() != "y":
        print("Exiting...")
        exit()
    print("The following configuration will be used:")
    print(f"Limit: {limit}")
    print(f"File Path: {file_path}")
    print(f"Initial Page: {initial_page}")
    confirm = input("Do you want to proceed with the configuration? (y/n): ")
    if confirm.lower() != "y":
        print("Exiting...")
        exit()
    # If a final message is provided, print it
    if final_message is not None:
        print(final_message + "\n")

def check_path_is_full_and_confirm(path, artist_name, suffix):
    total_path = path + artist_name.lower().replace(" ", "_") + suffix
    if os.path.exists(total_path):
        confirm = input(f"File {total_path} already exists. Do you want to overwrite it? (y/n): ")
        if confirm.lower() != "y":
            return False
        # Save a backup of the file
        run_number = get_run_number(path)
        if not os.path.exists(path + "backup" + f"/run_{run_number}"):
            os.mkdir(path + "backup" + f"/run_{run_number}")
        os.rename(total_path, path + "backup/" + f"run_{run_number}/{artist_name.lower().replace(' ', '_')}_songs.json")
    return True
    
def get_run_number(file_path):
    run_number = 1
    while os.path.exists(file_path + "backup/" + f"run_{run_number}"):
        run_number += 1
    return run_number

def filter_repeat_songs(file_path, filtered_file_path, artist):
    # Open the artits song file
    with open(file_path + artist.lower().replace(" ", "_") + "_songs.json", "r") as file:
        songs_json = json.load(file)
    # Create a dictionary to store the filtered songs
    filtered_songs = {}
    seen_song_names = set()
    for song_id, song_data in songs_json.items():
        normalized_name = normalize_song_name(song_data["song_name"])
        if normalized_name not in seen_song_names:
            filtered_songs[song_id] = song_data
            seen_song_names.add(normalized_name)
    # Save the filtered songs
    with open(filtered_file_path + artist.lower().replace(" ", "_") + "_songs.json", "w") as file:
        json.dump(filtered_songs, file, indent=4)



if __name__ == "__main__":
    ################################################
    ################ CONFIGURATION ################
    # Set the aritists name to gather all lyrics for
    artist_names = ["The Beatles", "Paul McCartney", "John Lennon", "Wings"]
    # Set the file path to save the data
    file_path = "artist_data/"
    # Set the file path to save the filtered data
    filtered_file_path = "artist_data_filtered/"
    # Set the file path to save the lyrics
    file_path_lyrics = "artist_lyrics/"
    # See if the user wants to filter the songs for no repeat. 
    filter_repeat = True
    
    ############## ADDITIONAL CONFIG ##############
    # Set the limit of songs to gather for each artist
    limit = 1
    # Set the initial page to start the search
    initial_page = 1
    ################ CONFIGURATION ################
    ################################################
    # Query user to ensure the artist names are correct and they want to proceed
    confirm_with_user(artist_names, limit, file_path, initial_page, final_message="Starting data gathering...")
    # Create the tqdm object
    pbar = tqdm(artist_names, total=len(artist_names))

    # Perform a loop over the artists names to gather the JSON data
    # This json data contains: song id (from genius), song name, 
    # artist name, the artist id, the release date, and the album name
    for artist_name in pbar:
        pbar.set_description(f"Artist: {artist_name}") # Update the progress bar with the artist name
        # Check if the file already exists and if the user wants to overwrite it
        if not check_path_is_full_and_confirm(file_path, artist_name, "_songs.json"):
            continue
        genius = GeniusSearch() # Create a GeniusSearch object
        # Search and save the artist ids
        genius.search_and_save_artist_ids(artist_name, file_path, limit=limit, initial_page=initial_page, pbar=pbar)

    print("ID gathering finished.")
        
    # Filter the song for no repeat songs using the normalized song name
    if filter_repeat:
        print("Filtering repeat songs...")
        pbar = tqdm(artist_names, total=len(artist_names))
        for artist in pbar:
            pbar.set_description(f"Artist: {artist}")
            filter_repeat_songs(file_path, filtered_file_path, artist)
        # Set the correct path to start the lyrics gathering
        file_path = filtered_file_path
        print("Filtering finished.")

    # Using the file_path, file_path_lyrics, and get_lyrics function, gather the lyrics for each song
    for artist in artist_names:
        # Check if the file already exists and if the user wants to overwrite it
        if not check_path_is_full_and_confirm(file_path_lyrics, artist, "_lyrics.csv"):
            continue
        # Open the artist songs file
        with open(file_path + artist.lower().replace(" ", "_") + "_songs.json", "r") as file:
            songs_json = json.load(file)
        # Create a dataframe to store all the data
        df = pd.DataFrame(songs_json).T
        # Create a pbar object which will iterate over the dataframe
        pbar = tqdm(df.iterrows(), total=len(df))
        # Create an empty list to store the lyrics
        lyrics_list = []
        # Iterate over the dataframe
        for index, row in pbar:
            pbar.set_description(f"Artist: {artist}")
            # Get the song id, which is the index
            lyrics = get_lyrics(index, GeniusSearch())
            lyrics_list.append(lyrics)
        # Add the lyrics to the dataframe
        df["Lyrics"] = lyrics_list
        # Save the dataframe to a csv file
        df.to_csv(file_path_lyrics + artist.lower().replace(" ", "_") + "_lyrics.csv", index=False)
    print("Lyrics gathering finished.")

    if "The Beatles" not in  artist_names:
        print("Data gathering finished.")
    else:
        # Start beatles specific data processing
        process_beatles_data(file_path_lyrics)
        print("Data gathering finished.")


    


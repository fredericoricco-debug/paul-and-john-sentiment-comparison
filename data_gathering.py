# General import
from tqdm import tqdm
import os

# My classes
from data_gathering_helpers.genius_api import GeniusSearch

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

def check_path_is_full_and_confirm(path, artist_name):
    total_path = path + artist_name.lower().replace(" ", "_") + "_songs.json"
    if os.path.exists(total_path):
        confirm = input(f"File {total_path} already exists. Do you want to overwrite it? (y/n): ")
        if confirm.lower() != "y":
            return False
    return True
    

if __name__ == "__main__":
    ################################################
    ################ CONFIGURATION ################
    # Set the aritists name to gather all lyrics for
    artist_names = ["The Beatles", "Paul McCartney", "John Lennon", "Wings"]
    # Set the file path to save the data
    file_path = "artist_data/"
    
    ############## ADDITIONAL CONFIG ##############
    # Set the limit of songs to gather for each artist
    limit = None
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
        if not check_path_is_full_and_confirm(file_path, artist_name):
            continue
        genius = GeniusSearch() # Create a GeniusSearch object
        # Search and save the artist ids
        genius.search_and_save_artist_ids(artist_name, file_path, limit=limit, initial_page=initial_page, pbar=pbar)
        


# imports
import requests
import json
import time
from bs4 import BeautifulSoup
import re
import random

class GeniusSearch:
    def __init__(self, token=None):
        # If the token is None, get it from the config file
        if token is None:
            self.token = self.get_token()
        else:
            self.token = token
        # Create the headers for the request
        self.headers = {
            "Authorization": "Bearer " + self.token
        }

    def get_token(self):
        # Open the config file and read the token
        with open("config.json", "r") as file:
            json_data = json.load(file)
            token = json_data["token"]
        return token

    def get_artist_id(self, artist_name):
        '''
        This function gets the artist id from the Genius API
        :param artist_name: The name of the artist
        :type artist_name: str

        :return: The artist id, the artist name
        :rtype: int
        :rtype: str
        '''
        # Create the request
        url = "https://api.genius.com/search?q=" + artist_name
        response = requests.get(url, headers=self.headers)
        # Artist id list
        artist_ids = []
        # Artists names
        artits_names = []
        # Iterate through the response and add the id and names to the list
        for hit in response.json()["response"]["hits"]:
            artist_ids.append(hit["result"]["primary_artist"]["id"])
            artits_names.append(hit["result"]["primary_artist"]["name"])
        # Find the artist id which is most common in the list
        # check if the name of the id corresponds to the artist name
        artist_id = None
        for i in range(len(artist_ids)):
            if artits_names[i].lower() == artist_name.lower():
                artist_id = artist_ids[i]
                break
        # If it is not found, return the most common id
        if artist_id is None:
            artist_id = max(set(artist_ids), key=artist_ids.count)
        # Get the artist name corresponding to the id
        artist_name = artits_names[artist_ids.index(artist_id)]
        # Return the artist id
        return artist_id, artist_name

    def search_keyword(self, keyword, limit=None):
        # Create the request
        url = "https://api.genius.com/search?q=" + keyword
        response = requests.get(url, headers=self.headers)
        # If the limit is None, return the response
        if limit is None:
            return response.json()
        else:
            # If the limit is not None, return the response with the limit
            return response.json()["response"]["hits"][:limit]

    def extract_song_ids(self, response, artist_id, dictionary = {}):
        '''
        This function extracts the song ids from the response
        :param response: The response from the Genius API
        :type response: dict

        :return: A dictionary where keys are the song ids and value is a dict
        with song names, artist name, song title, release date components
        :rtype: dict
        '''
        # Iterate through the response and add the song ids to the dictionary
        for song in response["response"]["songs"]:
            new_artist_id = song["primary_artist"]["id"]
            if new_artist_id != artist_id:
                continue
            song_id = song["id"]
            dictionary[song_id] = {
                "song_name": song["title"],
                "artist_name": song["primary_artist"]["name"],
                "artist_id": new_artist_id,
                "release_date": song["release_date_components"],
            }
            try:
                dictionary[song_id]["album_name"] = self.get_album_name(song_id)
            except:
                dictionary[song_id]["album_name"] = None
        # Return the dictionary
        return dictionary

    def get_album_name(self, song_id):
        # Sleep for a random amount of time between 1 and 2 seconds
        random_time = random.uniform(1, 2)
        time.sleep(random_time)
        # Create the request
        url = f"https://api.genius.com/songs/{song_id}"
        response = requests.get(url, headers=self.headers)
        # If the response status code is 200, return the album name
        if response.status_code == 200:
            try:
                album_name = response.json()["response"]["song"]["album"]["name"]
                return album_name
            except:
                return None
        else:
            # If the response status code is not 200, return None
            return None

    def get_all_artist_songs(self, artist_id, results_per_page=50, results_limit=None, initial_page = 1, pbar=None):
        # Create empty dictionary
        dictionary = {}
        # Starting page
        page = initial_page
        # Create the request
        blank_url = f"https://api.genius.com/artists/{artist_id}/songs?per_page={results_per_page}&page={page}"
        response = requests.get(blank_url, headers=self.headers)
        while True:
            if pbar is not None:
                # Set one of the progress bar's descriptions to the page number
                # But not the main one, as it will be overwritten by the artist name
                pbar.set_postfix({"Page": page})
            # If the response status code is 200, extract the song ids
            if response.status_code == 200:
                dictionary = self.extract_song_ids(response.json(), artist_id, dictionary)
                # If the limit is not None and the dictionary length is greater than the limit, break
                if results_limit is not None and len(dictionary) >= results_limit:
                    # Remove the extra songs
                    dictionary = {k: v for k, v in dictionary.items() if k in list(dictionary.keys())[:results_limit]}
                    print(f"Page {page} finished processing and truncated final results.")
                    break
                # If the response is empty, break
                if len(response.json()["response"]["songs"]) == 0:
                    print(f"Page {page} contained no results.")
                    break
                # Increment the page
                page += 1
                # Create the request
                url = f"https://api.genius.com/artists/{artist_id}/songs?per_page={results_per_page}&page={page}"
                response = requests.get(url, headers=self.headers)
                # Sleep for a random amount of time between 1 and 2 seconds
                random_time = random.uniform(1, 2)
                time.sleep(random_time)
            else:
                # If the response status code is not 200, break
                break 
            # Set the progress bar description to the number of songs found so far
            if pbar is not None:
                # Set one of the progress bar's descriptions to the page number
                # But not the main one, as it will be overwritten by the artist name
                pbar.set_postfix({"Songs Found": len(dictionary)})
        # Return the dictionary
        return dictionary

    def search_and_save_artist_ids(self, artist_name, file_path, limit=None, initial_page = 1, pbar=None):
        # Get the artist id
        artist_id, name = self.get_artist_id(artist_name)
        # Get the artist songs
        songs = self.get_all_artist_songs(artist_id, results_limit=limit, initial_page=initial_page, pbar=pbar)
        # Save the songs to a file
        with open(file_path + name.lower().replace(" ", "_") + "_songs.json", "w") as file:
            json.dump(songs, file, indent=4)

    def get_song_lyrics(self, song_id):
        # Create the request
        url = f"https://api.genius.com/songs/{song_id}"
        response = requests.get(url, headers=self.headers)
        # If the response status code is 200, return the lyrics
        if response.status_code == 200:
            path = response.json()["response"]["song"]["path"]
            # Create the request
            url = f"https://genius.com{path}"
            page = requests.get(url)
            # If the response status code is 200, return the lyrics
            if response.status_code == 200:
                html = BeautifulSoup(page.text, "html.parser")
                divs = html.find_all("div", class_=re.compile("^lyrics$|Lyrics__Container"))
                    # This function ensures spaces are correctly inserted between elements
                def add_space(element):
                    text = ' '.join(element.stripped_strings)
                    return text.replace(' ]', ']').replace('[ ', '[')  # Clean up bracket spacing

                lyrics = "\n".join([add_space(div) for div in divs])
                lyrics = re.sub(r'(\[.*?\])*', '', lyrics)
                lyrics = re.sub('\n{2}', '\n', lyrics)  # Reduce gaps between verses
                return lyrics.strip("\n")
            else: 
                # If the response status code is not 200, return None
                return None
        else:
            # If the response status code is not 200, return None
            return None

def get_lyrics(id, genius_object):
    # get the lyrics
    lyrics = genius_object.get_song_lyrics(id)
    # return the lyrics
    return lyrics

if __name__ == "__main__":
    # Create a GeniusSearch object
    genius = GeniusSearch()
    # Get the lyrics for the song with id 123444
    lyrics = get_lyrics(123444, genius)
    # Print the lyrics
    print(lyrics)

    
    

    



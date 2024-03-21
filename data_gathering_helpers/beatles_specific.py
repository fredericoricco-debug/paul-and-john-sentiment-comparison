# Imports
from bs4 import BeautifulSoup
import pandas as pd
from nltk.metrics import jaccard_distance
from nltk.util import ngrams
import unidecode

# CONFIG
beatles_path = 'beatles_data/'
webpage_path = "beatles_webpage/webpage.html"

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

# Normalize text function
def normalize_text(text):
    text = unidecode.unidecode(text)  # Normalize UTF-8 characters to ASCII
    text = text.lower()  # Convert to lowercase
    return text

def process_beatles_data(lyrics_csv_path):
    with open(webpage_path, "r") as file:
        webpage = file.read()
    
    soup = BeautifulSoup(webpage, "html.parser")
    tables = soup.find_all("table")

    data = []
    for table in tables:
        for row in table.find_all("tr"):
            columns = row.find_all("td")
            if len(columns) > 0:
                song = columns[0].text.strip()
                composer = columns[1].text.strip()
                if composer in ["Lennon", "McCartney"]:
                    data.append({"Song": song, "Composer": composer})

    df = pd.DataFrame(data)
    df_with_lyrics = pd.read_csv(lyrics_csv_path + "the_beatles_lyrics.csv")

    matched_rows = []
    for index, song_composer in df.iterrows():
        best_match = None
        highest_similarity = 0
        for index2, song_no_composer in df_with_lyrics.iterrows():
            similarity = calculate_similarity(song_composer["Song"], song_no_composer["song_name"])
            if similarity > highest_similarity:
                highest_similarity = similarity
                best_match = song_no_composer

        if best_match is not None:
            row = {
                "song_name": best_match["song_name"],
                "composer": song_composer["Composer"],
                "release_date": best_match["release_date"],
                "album_name": best_match["album_name"],
                "lyrics": best_match["Lyrics"]
            }
            matched_rows.append(row)

    # save the data
    df_matched = pd.DataFrame(matched_rows)
    df_matched.to_csv(beatles_path + "beatles_data.csv", index=False)
        

if __name__ == "__main__":
    process_beatles_data("artist_lyrics/")
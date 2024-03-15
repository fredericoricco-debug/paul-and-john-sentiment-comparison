import json
import pandas as pd

# Load the data
df = pd.read_csv("beatles_songs.csv")
# Read the beatles songs data
with open("artist_data/the_beatles_songs.json", "r") as file:
    beatles_songs = json.load(file)

# Drop the "Singer" column from the dataframe
df = df.drop("Singer", axis=1)

# 
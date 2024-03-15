# imports
import requests
from bs4 import BeautifulSoup
import pandas as pd

url = "http://www.beatlesarchive.net/composer-singer-beatles-songs.html"

# Get the page content
page_content = requests.get(url).content

# Create a BeautifulSoup object
soup = BeautifulSoup(page_content, "html.parser")

# Get all the tables    
tables = soup.find_all("table")

# Create an empty dataframe
df = pd.DataFrame(columns=["Song", "Composer", "Singer"])

# Go through each table, saving the data in the dataframe
for table in tables:
    for row in table.find_all("tr"):
        columns = row.find_all("td")
        if len(columns) > 0:
            song = columns[0].text
            composer = columns[1].text
            singer = columns[2].text
            row = {"Song": song, "Composer": composer, "Singer": singer}
            # Use concat
            df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)

# Save the dataframe to a csv file
df.to_csv("beatles_songs.csv", index=False)
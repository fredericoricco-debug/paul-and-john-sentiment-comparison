import re
from transformers import pipeline
import pandas as pd
from tqdm import tqdm

# Constants
love = "love"
# ooh, woo, tchic, nananana, mm, da, ah, hoo, la, oh, and tit
singing = ["ooh", "la", "nananana", "oh", "ah", "woo", "tchic", "mm", "da", "hoo", "tit"]

remove_love = True
remove_singing = True

data_path = "beatles_songs_with_ids.csv"
# Load the sentiment-analysis model
classifier = pipeline("zero-shot-classification")
my_labels = ['very negative', 'negative', 'neutral', 'positive', 'very positive']

def split_lyrics(lyrics, chunk_size=512):
    words = lyrics.split()
    chunks = []
    current_chunk = []

    for word in words:
        if len(" ".join(current_chunk)) + len(word) + 1 <= chunk_size:
            current_chunk.append(word)
        else:
            chunks.append(" ".join(current_chunk))
            current_chunk = [word]

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks

# Get the data from the dataframe
dataframe = pd.read_csv(data_path)

# perform word removal
if remove_love:
    dataframe["Lyrics"] = dataframe["Lyrics"].apply(lambda x: re.sub(r"\b" + love + r"\b", "", x, flags=re.IGNORECASE))
if remove_singing:
    for word in singing:
        pattern = r"\b" + word + r"\b"
        dataframe["Lyrics"] = dataframe["Lyrics"].apply(lambda x: re.sub(pattern, "", x, flags=re.IGNORECASE))


# Add two new columns to the dataframe: "Sentiment" and "Sentiment Score"
dataframe["Sentiment"] = ""
dataframe["Sentiment Score"] = 0.0

# Mapping from sentiment labels to scores
sentiment_scores = {
    'very negative': -1,
    'negative': -0.5,
    'neutral': 0,
    'positive': 0.5,
    'very positive': 1
}

# For each row in the dataframe, get the sentiment and the sentiment score for the lyrics
for index, row in tqdm(dataframe.iterrows(), total=len(dataframe)):
    lyrics = row["Lyrics"]
    
    # Split the lyrics into chunks using the split_lyrics function
    chunks = split_lyrics(lyrics)
    
    # Initialize variables to store cumulative scores and total count for averaging
    cumulative_score = 0
    total_chunks = len(chunks)
    
    # Analyze the sentiment of each chunk
    for chunk in chunks:
        sentiments = classifier(chunk, candidate_labels=my_labels)
        chunk_score = 0
        for label, score in zip(sentiments["labels"], sentiments["scores"]):
            chunk_score += score * sentiment_scores[label]
        # Update cumulative score with the weighted chunk score
        cumulative_score += chunk_score

    # Calculate the average score for the song and assign it to the dataframe
    final_score = cumulative_score / total_chunks if total_chunks > 0 else 0
    dataframe.at[index, "Sentiment Score"] = final_score

# Save the updated dataframe
dataframe.to_csv("beatles_songs_with_sentiment_zero_shot.csv", index=False)
import re
from transformers import pipeline
import pandas as pd
from tqdm import tqdm

# Constants
love = "love"
# ooh, woo, tchic, nananana, mm, da, ah, hoo, la, oh, and tit
singing = ["ooh", "la", "nananana", "oh", "ah", "woo", "tchic", "mm", "da", "hoo", "tit"]

remove_love = False
remove_singing = True

data_path = "beatles_songs_with_ids.csv"
# Load the sentiment-analysis model
sentiment_analysis = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")

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

# For each row in the dataframe, get the sentiment and the sentiment score for the lyrics
for index, row in tqdm(dataframe.iterrows(), total=len(dataframe)):
    lyrics = row["Lyrics"]
    
    # Split the lyrics into chunks using the split_lyrics function
    chunks = split_lyrics(lyrics)
    
    # Analyze the sentiment of each chunk
    sentiments = sentiment_analysis(chunks)
    
    # Normalize the sentiment scores and calculate the weights
    normalized_scores = []
    weights = []
    total_words = sum(len(chunk.split()) for chunk in chunks)
    
    for sentiment, chunk in zip(sentiments, chunks):
        if sentiment["label"] == "POSITIVE":
            normalized_score = sentiment["score"]
        else:
            normalized_score = -sentiment["score"]
        normalized_scores.append(normalized_score)
        
        chunk_words = len(chunk.split())
        weight = chunk_words / total_words
        weights.append(weight)
    
    # Calculate the weighted average normalized sentiment score
    weighted_score = sum(score * weight for score, weight in zip(normalized_scores, weights))
    
    # Determine the overall sentiment based on the sign of the weighted score
    overall_sentiment = "POSITIVE" if weighted_score >= 0 else "NEGATIVE"
    
    dataframe.at[index, "Sentiment"] = overall_sentiment
    dataframe.at[index, "Sentiment Score"] = weighted_score

# Save the updated dataframe
dataframe.to_csv("beatles_songs_with_sentiment.csv", index=False)
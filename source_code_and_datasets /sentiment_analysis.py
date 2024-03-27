import re, os 
from transformers import pipeline
import pandas as pd
import datetime
from tqdm import tqdm

# ooh, woo, tchic, nananana, mm, da, ah, h
singing = ["ooh", "la", "nananana", "oh", "ah", "woo", "tchic", "mm", "da", "hoo", "tit"]

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

def perform_sentiment_analysis(labels, mapping, data_path, remove_love, remove_singing):
    # Load the sentiment-analysis model
    classifier = pipeline("zero-shot-classification")

    # Get the data from the dataframe
    dataframe = pd.read_csv(data_path)

    # If the dataframe has a column with "Lyrics" change it to "lyrics"
    if "Lyrics" in dataframe.columns:
        dataframe.rename(columns={"Lyrics": "lyrics"}, inplace=True)

    # perform word removal
    if remove_love:
        dataframe["lyrics"] = dataframe["lyrics"].fillna("").apply(lambda x: re.sub(r"\b" + "love" + r"\b", "", x, flags=re.IGNORECASE))
    if remove_singing:
        for word in singing:
            pattern = r"\b" + word + r"\b"
            dataframe["lyrics"] = dataframe["lyrics"].fillna("").apply(lambda x: re.sub(pattern, "", x, flags=re.IGNORECASE))


    # Add two new columns to the dataframe: "Sentiment" and "Sentiment Score"
    dataframe["Category"] = ""
    dataframe["Category Score"] = 0.0

    # For each row in the dataframe, get the sentiment and the sentiment score for the lyrics
    for index, row in tqdm(dataframe.iterrows(), total=len(dataframe)):
        lyrics = row["lyrics"]
        
        # Split the lyrics into chunks using the split_lyrics function
        chunks = split_lyrics(lyrics)
        
        # Initialize variables to store cumulative scores and total count for averaging
        cumulative_score = 0
        total_chunks = len(chunks)
        
        # Analyze the sentiment of each chunk
        for chunk in chunks:
            sentiments = classifier(chunk, candidate_labels=labels)
            chunk_score = 0
            for label, score in zip(sentiments["labels"], sentiments["scores"]):
                chunk_score += score * mapping[label]
            # Update cumulative score with the weighted chunk score
            cumulative_score += chunk_score

        # Calculate the average score for the song and assign it to the dataframe
        final_score = cumulative_score / total_chunks if total_chunks > 0 else 0
        dataframe.at[index, "Category Score"] = final_score
        # Set the category based on the final score using the mapping dictionary
        # Find the number closest to the final score in the mapping dictionary
        closest_score = min(mapping.values(), key=lambda x:abs(x-final_score))
        # Get the category corresponding to the closest score
        category = [key for key, value in mapping.items() if value == closest_score][0]
        # Assign the category to the dataframe
        dataframe.at[index, "Category"] = category
        
    # return the dataframe
    return dataframe
    


if __name__ == "__main__":
    # Set labels
    my_labels = ['very negative', 'negative', 'neutral', 'positive', 'very positive']
    # Mapping from sentiment labels to scores
    mapping = {
        'very negative': -1,
        'negative': -0.5,
        'neutral': 0,
        'positive': 0.5,
        'very positive': 1
    }
    # Get path from the user
    data_path = input("Enter the path to the data file: ")
    # Check it exists if not print message and exit
    if not os.path.exists(data_path):
        print("File does not exist.")
        exit()
    
    # Perform sentiment analysis
    result = perform_sentiment_analysis(my_labels, mapping, data_path, remove_love=False, remove_singing=True)

    # Get the time and date for a unique filename
    now = datetime.datetime.now()

    # Save the result to a new CSV file
    result.to_csv(f"sentiment_scores/sentiment_analysis_{now.strftime('%Y-%m-%d_%H-%M-%S')}.csv", index=False)

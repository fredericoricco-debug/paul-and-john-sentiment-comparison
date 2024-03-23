# Imports
import os
import pandas as pd
from datetime import datetime
from ast import literal_eval

from collections import Counter
import nltk
from nltk.tokenize import word_tokenize
from wordcloud import WordCloud, STOPWORDS
from nltk.corpus import wordnet
from nltk import pos_tag
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import spacy

# Plotting stuffs
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.dates as mdates

# Significant historical events dictionary
history = {"Kennedy Assassination": "1963-11-22", "Civil Rights Act": "1964-07-02", 'The Voting Rights Act': '1965-08-06', "Moon Landing": "1969-07-20"}

nlp = spacy.load("en_core_web_sm")

# Define a function to convert between NLTK's POS tags and wordnet's POS tags
def get_wordnet_pos(treebank_tag):
    if treebank_tag.startswith('J'):
        return wordnet.ADJ
    elif treebank_tag.startswith('V'):
        return wordnet.VERB
    elif treebank_tag.startswith('N'):
        return wordnet.NOUN
    elif treebank_tag.startswith('R'):
        return wordnet.ADV
    else:
        return None

# Function to process lyrics: tokenize, remove stopwords, and return words
def process_lyrics(lyrics, stopwords_set):
    words = word_tokenize(lyrics.lower())
    filtered_words = [word for word in words if word.isalpha() and word not in stopwords_set]
    return filtered_words

def create_distribution_plot(data):
    # Assuming 'data' is a DataFrame with the same structure as the one we've used
    # Filter to include only rows with composers McCartney and Lennon
    filtered_data = data[data['composer'].isin(['McCartney', 'Lennon'])]
    
    # Set the aesthetic style of the plots
    sns.set_theme(style="whitegrid")
    
    # Create the violin plot
    plt.figure(figsize=(10, 6))
    ax = sns.violinplot(x=filtered_data['composer'], y=filtered_data['Category Score'], inner='quartile')
    
    # Setting the y-axis limits from -1 to 1
    ax.set_ylim(-1, 1)
    
    # Adding titles and labels
    plt.title('Distribution of Sentiment Scores by Composer', fontsize=16)
    plt.xlabel('Composer', fontsize=14)
    plt.ylabel('Category Score', fontsize=14)
    
    # Save the plot as an image, using the time and date as part of the filename
    now = datetime.now()
    plt.savefig(f'plots/distribution_plot_{now.strftime("%Y-%m-%d_%H-%M-%S")}.png')

def create_unique_word_cloud(data):
    stopwords_set = set(spacy.lang.en.stop_words.STOP_WORDS) | set(STOPWORDS)
    
    # Process lyrics for each composer using SpaCy
    mccartney_lyrics = ' '.join(data[data['composer'] == 'McCartney']['lyrics'])
    lennon_lyrics = ' '.join(data[data['composer'] == 'Lennon']['lyrics'])
    
    # Process the lyrics
    mccartney_words = process_lyrics(mccartney_lyrics, stopwords_set)
    lennon_words = process_lyrics(lennon_lyrics, stopwords_set)

    # Identify common words
    common_words = set(mccartney_words) & set(lennon_words)

    # Remove common words from each set
    mccartney_unique = [word for word in mccartney_words if word not in common_words]
    lennon_unique = [word for word in lennon_words if word not in common_words]

    # Covert them back to strings
    mccartney_unique = ' '.join(mccartney_unique)
    lennon_unique = ' '.join(lennon_unique)

    mccartney_doc = nlp(mccartney_unique)
    lennon_doc = nlp(lennon_unique)
    
    # Extract adjectives using SpaCy's POS tagging
    mccartney_adjectives = [token.text for token in mccartney_doc if token.pos_ == 'ADJ' and token.text not in stopwords_set]
    lennon_adjectives = [token.text for token in lennon_doc if token.pos_ == 'ADJ' and token.text not in stopwords_set]
    
    # Count frequency of adjectives
    mccartney_adjectives_freq = Counter(mccartney_adjectives)
    lennon_adjectives_freq = Counter(lennon_adjectives)
    
    # Generate and display word clouds
    mccartney_wordcloud = WordCloud(background_color ='white').generate_from_frequencies(mccartney_adjectives_freq)
    lennon_wordcloud = WordCloud(background_color ='white').generate_from_frequencies(lennon_adjectives_freq)
    
    plt.figure(figsize=(10, 5))
    
    plt.subplot(1, 2, 1)
    plt.imshow(mccartney_wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.title('McCartney Unique Adjectives')
    
    plt.subplot(1, 2, 2)
    plt.imshow(lennon_wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.title('Lennon Unique Adjectives')

    # Save the plot as an image, using the time and date as part of the filename
    now = datetime.now()
    plt.savefig(f'plots/unique_wordcloud_{now.strftime("%Y-%m-%d_%H-%M-%S")}.png')

# Refined approach to handle potential None values or other anomalies in the data
def refined_literal_date_parse(date_str):
    try:
        date_dict = literal_eval(date_str)
        if all(key in date_dict for key in ['year', 'month', 'day']):
            return datetime(year=int(date_dict['year']), month=int(date_dict['month']), day=int(date_dict['day']))
        else:
            return None
    except:
        return None

# Function to calculate and plot moving average of sentiment scores with specified granularity
def calculate_and_plot_moving_average(data, months):
    # Convert release_date to datetime
    data['release_date'] = data['release_date'].apply(refined_literal_date_parse)
    data['year_month'] = data['release_date'].dt.to_period('M')
    
    # Group by composer and year_month, then calculate the average Category Score
    grouped_data = data.groupby(['composer', 'year_month'])['Category Score'].mean().reset_index()

    # Calculate moving average
    grouped_data['moving_average'] = grouped_data.groupby('composer')['Category Score'].transform(lambda x: x.rolling(window=months, min_periods=1).mean())

    # Plotting
    plt.figure(figsize=(14, 7))
    for composer in ['Lennon', 'McCartney']:
        subset = grouped_data[grouped_data['composer'] == composer]
        plt.plot(pd.to_datetime(subset['year_month'].astype(str)), subset['moving_average'], label=f'{composer} {months}-Month MA')

    now = datetime.now()

    plt.title(f'{months}-Month Moving Average of Sentiment Scores')
    plt.xlabel('Date')
    plt.ylabel('Moving Average of Sentiment Score')
    plt.legend()
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.savefig(f'plots/moving_average_{months}_{now.strftime("%Y-%m-%d_%H-%M-%S")}.png')

def calculate_and_plot_moving_average_historical(data, months, history):
    # Convert release_date to datetime
    data['release_date'] = data['release_date'].apply(refined_literal_date_parse)
    data['year_month'] = data['release_date'].dt.to_period('M')
    
    # Group by composer and year_month, then calculate the average Category Score
    grouped_data = data.groupby(['composer', 'year_month'])['Category Score'].mean().reset_index()

    # Calculate moving average
    grouped_data['moving_average'] = grouped_data.groupby('composer')['Category Score'].transform(lambda x: x.rolling(window=months, min_periods=1).mean())

    # Plotting
    plt.figure(figsize=(14, 7))
    for composer in ['Lennon', 'McCartney']:
        subset = grouped_data[grouped_data['composer'] == composer]
        plt.plot(pd.to_datetime(subset['year_month'].astype(str)), subset['moving_average'], label=f'{composer} {months}-Month MA')

    # Plot historical events
    for event, date in history.items():
        event_date = datetime.strptime(date, "%Y-%m-%d")
        plt.axvline(x=event_date, color='k', linestyle='--')
        plt.text(event_date + pd.to_timedelta(15, 'D'), plt.ylim()[1] - 0.05 * (plt.ylim()[1] - plt.ylim()[0]), event, rotation=90, verticalalignment='top')

    now = datetime.now()

    plt.title(f'{months}-Month Moving Average of Sentiment Scores with Historical Events')
    plt.xlabel('Date')
    plt.ylabel('Moving Average of Sentiment Score')
    plt.legend()
    plt.grid(True)
    plt.xticks(rotation=45)

    # Adjust x-axis to better fit event labels
    plt.gca().xaxis.set_major_locator(mdates.YearLocator())
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    
    plt.tight_layout()
    plt.savefig(f'plots/moving_average_historical_{months}_{now.strftime("%Y-%m-%d_%H-%M-%S")}.png')

if __name__ == "__main__":
    # Downloads
    #nltk.download('punkt')
    #nltk.download('averaged_perceptron_tagger')
    #nltk.download('stopwords')
    #nltk.download('wordnet')
    ### CONFIG ###
    perform_distribution = False
    perform_unique_cloud = False
    perform_moving_average = False
    perform_historical_events = True
    path = "sentiment_scores/sentiment_analysis_2024-03-21_18-50-18.csv"
    ##############
    # Check if the path is empty
    if path == None or path == "" or not os.path.exists(path):
        path = input("Enter the path to the sentiment dataset: ")
        # Check if the file exists
        if not os.path.exists(path):
            print("File does not exist.")
            exit()
    # Load the dataset
    data = pd.read_csv(path)

    # Perform distribution plot?
    if perform_distribution:
        create_distribution_plot(data)

    # Perform unique word cloud?
    if perform_unique_cloud:
        create_unique_word_cloud(data)

    # Perform evolution of scores over time?
    if perform_moving_average:
        calculate_and_plot_moving_average(data, 6)

    # Perform evolution of scores over time with historical events?
    if perform_historical_events:
        calculate_and_plot_moving_average_historical(data, 6, history)
        
    


    

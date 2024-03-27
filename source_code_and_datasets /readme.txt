DATASETS:

The dataset with raw lyrical data is present in artist_lyrics/the_beatles_lyrics.csv, this data is used to perform sentiment analysis.
The final data set used for visualisations is present in sentiment_scores/sentiment_analysis_beatles.csv.

INSTRUCTION TO USE THE TOOL:

First ensure the root directory is "source_code_and_datasets" not the directory containing the report.

To use this tool, please go to: https://docs.genius.com/#/getting-started-h1 and follow the instructions to get your API key. 

Once you have the API token, fill the config.json file with the token.

1. Run the data_gathering tool to fill the artist_data, the artist_data_filtered, and the artist_lyrics folders with the data of the artists you want to analyze.
2. Run the sentiment_analysis tool to fill the sentiment_analysis folder with the sentiment analysis of the lyrics of the artists you want to analyze.
3. If you're analysing Paul McCartney vs. John Lennon, please run the data_interpretation tool to produce plots. (You can also easily compare other artists by modifying the code in the data_interpretation tool.)

Thanks!
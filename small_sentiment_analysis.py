from transformers import pipeline

neutral_sentence = ""

singing = ["ooh", "la", "nananana", "oh", "ah", "woo", "tchic", "mm", "da", "hoo", "tit"]

sentiment_analysis = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")

print(sentiment_analysis(neutral_sentence))

# for each word, print out the word and the sentiment label and score all in one line
for word in singing:
    pass
    #sentiment = sentiment_analysis(word)
    #print(f"{word}, {sentiment[0]['label']}, {sentiment[0]['score']}")
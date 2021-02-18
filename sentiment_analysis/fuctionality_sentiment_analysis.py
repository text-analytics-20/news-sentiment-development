import json
from sentiment_analysis.sentimentDictionary import SentimentDictionary 

def analyse_sentiment(text: str, listSearchTerms: list ) -> float:
    if not any([searchTerm in text.lower() for searchTerm in listSearchTerms]):
        return 0.0
    sd = SentimentDictionary()
    sd.predict_sentiment(text, listSearchTerms ,True)
    #sentences="Sentences: ", sd.sentencesWithSentiment)
    return sd.sentimentText

listSearchTerm=["flüchtling", "geflüchtete", "refugee"]



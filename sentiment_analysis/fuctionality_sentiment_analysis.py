import json
from sentiment_analysis.sentimentDictionary import sentimentDictionary 

def analyse_sentiment(text: str, listSearchTerms: list ) -> float:
    if not any([searchTerm in text.lower() for searchTerm in listSearchTerms]):
        return 0.0
    sd = sentimentDictionary()
    sd.predict_sentiment(text, listSearchTerms ,True)
    #print("Sentences: ", sd.sentencesWithSentiment)
    return sd.sentimentText

listSearchTerm=["flüchtling", "geflüchteter", "refugee"]



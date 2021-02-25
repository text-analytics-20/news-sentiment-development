import spacy
from spacy_sentiws import spaCySentiWS
from sentiment_analysis.negation_handling import *

# class that ranks sentiment based on a dictionary approach
# based on sentiws by the leipzig university
#   see: https://wortschatz.uni-leipzig.de/en/download
# implemented using a singleton pattern


class SentimentDictionary():
    __instance = None

    @staticmethod
    def getInstance():
        """ Static access method. """
        if SentimentDictionary.__instance == None:
            SentimentDictionary()
        return SentimentDictionary.__instance

    def __init__(self):
        """ Virtually private constructor. """
        if SentimentDictionary.__instance != None:
            raise Exception("Class sentimentDictionary is a singleton!")
        else:
            SentimentDictionary.__instance = self

        # load spacy for german
        self.nlp = spacy.load('de')

        # loads the sentiment ws data
        self.sentiws = spaCySentiWS("data/sentiws")
        self.nlp.add_pipe(self.sentiws)

    sentimentText = 0.0
    sentencesWithSentiment = {}
    compound = {}
    sentimentTextIsAdditive = False
    saveSentencesWithSentiment = False

    # main function
    # takes the text and a list of search Terms
    def predict_sentiment(self, text: str, searchTermList: list) -> float:
       
        if not self.sentimentTextIsAdditive:
            # new sentiment is calculated for every function call
            self.sentimentText = 0.0

        # read the text into spacy
        doc = self.nlp(text)

        # the counter is used for normalization 
        counter = 0

        # iterate through all sentences in the document
        for sentence in doc.sents:
            sentenceText = sentence.text

            # to get a sentiment related to the search terms only sentences
            # containing a search term are evaluated
            if any(term in sentenceText.lower() for term in searchTermList):
                if sentenceText in self.sentencesWithSentiment:
                    # check that sentences are not entered twice
                    continue
                sentimentSentence = 0.0
                for word in sentence:
                    if any(term in word.text.lower() for term in searchTermList):
                        # The sentiment of search terms is neglected to reduce bias
                        self.count_this(self.compound, word.text)
                        continue
                    if word._.sentiws is not None:
                        counter += 1
                        # if word has a sentiment weight it is added to the sentiment value 
                        # and the counter in increased
                        sentimentSentence += float(word._.sentiws) * check_for_negation(sentence,word)
                if self.saveSentencesWithSentiment:
                    # save the sentences with sentiment 
                    self.count_this(self.sentencesWithSentiment, sentenceText, sentimentSentence)
                self.sentimentText += sentimentSentence
        if counter > 0:
            self.sentimentText /= counter 
        return self.sentimentText

    def count_this(self, dictionary: dict, key: str, value: float = 1.0):
        # adds the given value or 1 to the key in the provided dictionary
        # is used to count occourences of words or save the sentiment of sentences
        if key in dictionary:
            dictionary[key] += value
        else:
            dictionary[key] = value


def analyse_sentiment(text: str, search_terms: list) -> float:
    if not isinstance(text, str):
        raise TypeError(f"analyse sentiment takes a string")
    if not search_terms or not isinstance(search_terms, list) or not all(isinstance(entry, str) for entry in search_terms):
        raise TypeError(f"analyse sentiment takes a list of str")

    if not any([searchTerm in text.lower() for searchTerm in search_terms]):
        return 0.0
    sd = SentimentDictionary.getInstance()
    sd.predict_sentiment(text, search_terms)
    return sd.sentimentText


def test():
    texts = ["Flüchtlinge nehmen uns die Arbeitsplätze weg.",
             "Wir müssen uns gemeinsam anstregenen Flüchtlinge gut zu intigrieren.",
             "Wir schaffen das!", 
             "Flüchtlinge sind schlecht!", 
             "Flüchtlinge sind nicht schlecht!"]

    print("\n Sentiment analysis using sentiws:")
    for t in texts:
        print(t, analyse_sentiment(t, ["flüchtlinge"]))

if __name__ == "__main__":
    test()
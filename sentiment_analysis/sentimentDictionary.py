import spacy
from spacy_sentiws import spaCySentiWS
from sentiment_analysis.negation_handling import *

# class that ranks sentiment based on a dicitionary apporach
# based on Singelton pattern


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
    sentimentTextIsAdditiv = False
    saveSentencesWithSentiment = False

    def setSentimentTextAddititv(self, Boolean):
        # additiv sentiment can be enabled
        # if the text is to long to be read at once
        # or text is given piece by piece
        self.sentimentTextIsAdditiv = Boolean
    
    def saveSenteneces(self, Boolean):
        # per default sentences with sentiment are saved to check for double usage
        # This can be disabled for faster runtime or less memory usage
        self.saveSentencesWithSentiment = Boolean

    def predict_sentiment(self, text: str, searchTermList: list) -> float:
        if not self.sentimentTextIsAdditiv:
            # print("alkdfwj")
            # new sentiment is calculated for every function call
            self.sentimentText = 0.0
        doc = self.nlp(text)
        counter = 1
        for sentence in doc.sents:
            sentenceText = sentence.text
            if any(term in sentenceText.lower() for term in searchTermList):
                if sentenceText in self.sentencesWithSentiment:
                    continue
                # only work with sentences that contain the serachTerm
                sentimentSentence = 0.0
                for word in sentence:
                    if any(term in word.text.lower() for term in searchTermList):
                        # save the word that contained the serach term and skip sentiment analysis on this word
                        self.count_this(self.compound, word.text)
                        continue
                    if word._.sentiws is not None:
                        counter += 1
                        # if word has a sentiment weight it is added to the sentiment value 
                        sentimentSentence += float(word._.sentiws) * check_for_negation(sentence,word)
                        # print(word, word._.sentiws, check_for_negation(sentence,word))
                if self.saveSentencesWithSentiment:
                    self.count_this(self.sentencesWithSentiment, sentenceText, sentimentSentence)
                self.sentimentText += sentimentSentence
        return self.sentimentText/counter

    def count_this(self, dictionary: dict, key: str, value: float = 1.0):
        # adds the given value or 1 to the key in the provided dictionary
        # is used to count occourences of words or save the sentiment of sentences
        if key in dictionary:
            dictionary[key] += value
        else:
            dictionary[key] = value


def analyse_sentiment(text: str, listSearchTerms: list) -> float:
    if not any([searchTerm in text.lower() for searchTerm in listSearchTerms]):
        return 0.0
    sd = SentimentDictionary.getInstance()
    sd.predict_sentiment(text, listSearchTerms)
    return sd.sentimentText


if __name__ == "__main__":
    texts = ["Flüchtlinge nehmen uns die Arbeitsplätze weg.", "Wir müssen uns gemeinsam anstregenen Flüchtlinge gut zu intigrieren.", "Wir schaffen das!", "Flüchtlinge sind scheiße!", "Flüchtlinge sind nicht scheiße!"]
    for t in texts:
        print(t, analyse_sentiment(t, ["flüchtlinge"]))

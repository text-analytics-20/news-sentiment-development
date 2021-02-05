import spacy
from spacy_sentiws import spaCySentiWS

# class that ranks sentiment based on a dicitionary apporach
# based on Singelton pattern

class sentimentDictionary():
    __instance = None
    @staticmethod 
    def getInstance():
        """ Static access method. """
        if sentimentDictionary.__instance == None:
            sentimentDictionary()
        return sentimentDictionary.__instance

    def __init__(self):
        """ Virtually private constructor. """
        if sentimentDictionary.__instance != None:
            raise Exception("Class sentimentDictionary is a singleton!")
        else:
            sentimentDictionary.__instance = self

        # load spacy for german
        self.nlp = spacy.load('de')

        # loads the sentiment ws data
        self.sentiws = spaCySentiWS("data/sentiws")
        self.nlp.add_pipe(self.sentiws)


    sentimentText=0.0
    sentencesWithSentiment={}
    compound={}
    sentimentTextIsAdditiv=False
    saveSentencesWithSentiment=False 

    def setSentimentTextAddititv(self,Boolean):
        # additiv sentiment can be enabled if the text is to long to be read at once
        # or text is given piece by piece
        self.sentimentTextIsAdditiv=Boolean
    

    def saveSenteneces(self,Boolean):
        # per default sentences with sentiment are saved to check for double usage
        # This can be disabled for faster runtime or less memory usage
        self.saveSentencesWithSentiment=Boolean

    def predict_sentiment(self, text : str, searchTermList : list) -> float:
        if not self.sentimentTextIsAdditiv:
            sentimentText = 0.0 #makes sure that a new sentiment is calculated for every function call
        doc = self.nlp(text)
        for sentence in doc.sents:
            sentenceText = sentence.text
            if any(term in sentenceText.lower() for term in searchTermList):
                if sentimentText in self.sentencesWithSentiment:
                    continue
                # only work with sentences that contain the serachTerm
                sentimentSentence = 0.0
                for word in sentence:
                    if any(term in word.text.lower() for term in searchTermList):
                        # save the word that contained the serach term and skip sentiment analysis on this word
                        self.countThis(self.compound, word.text)
                        continue
                    if word._.sentiws!=None:
                        # if word has a sentiment weight it is added to the sentiment value 
                        sentimentSentence+=float(word._.sentiws)
                if self.saveSentencesWithSentiment:
                    self.countThis(self.sentencesWithSentiment, sentenceText, sentimentSentence)
                self.sentimentText+=sentimentSentence
        return self.sentimentText

    def countThis(self, dictionary : dict, key : str , value = 1):
        # adds the given value or 1 to the key in the provided dictionary
        # is used to count occourences of words or save the sentiment of sentences
        if key in dictionary:
            dictionary[key]+=value
        else:
            dictionary[key]=value

def analyse_sentiment(text: str, listSearchTerms: list ) -> float:
    if not any([searchTerm in text.lower() for searchTerm in listSearchTerms]):
        return 0.0
    sd = sentimentDictionary.getInstance()
    sd.predict_sentiment(text, listSearchTerms)
    #sentences="Sentences: ", sd.sentencesWithSentiment)
    return sd.sentimentText

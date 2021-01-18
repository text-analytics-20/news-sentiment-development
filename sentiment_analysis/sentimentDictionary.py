import spacy
from spacy_sentiws import spaCySentiWS

# class that ranks sentiment based on a dicitionary apporach
class sentimentDictionary():
    sentimentText=0.0
    sentencesWithSentiment={}
    compound={}

    def __init__(self, sentimentTextIsAdditiv=False): 
        self.nlp = spacy.load('de')

        # loads the sentiment ws data
        self.sentiws = spaCySentiWS("data/sentiws")
        self.nlp.add_pipe(self.sentiws)

        # additiv sentiment can be enabled if the text is to long to be read at once
        # or text is given piece by piece
        self.sentimentTextIsAdditiv=sentimentTextIsAdditiv 

    
    def predict_sentiment(self, text : str, searchTermList : str, saveSentencesWithSentiment = False) -> float:
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
                        # if word has a sentiment weight it is added to the sentimen value 
                        sentimentSentence+=float(word._.sentiws)
                if saveSentencesWithSentiment:
                    self.countThis(self.sentencesWithSentiment, sentenceText, sentimentSentence)
                self.sentimentText+=sentimentSentence


    def countThis(self, dictionary : dict, key : str , value = 1):
        # adds the given value or 1 to the key in the provided dictionary
        # is used to count occourences of words or save the sentiment of sentences
        if key in dictionary:
            dictionary[key]+=value
        else:
            dictionary[key]=value

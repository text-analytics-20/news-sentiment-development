import spacy
from nltk.stem.snowball import SnowballStemmer

stemmer = SnowballStemmer(language='german')

def check_for_negation(sentence, word):
    #checks if word in sentence is negated; BOTH (word and sentence) are already tokenized!
    #returns sign (+1: not negated, -1: negated)
	
	#TODO: handle case when word appears twice in the sentence
	#TODO: Improve by checking negation of complete phrase (=negation of verb)

    neg_words = ['nicht', 'kein', 'nirgends', 'nirgendwo', 'niemand', 'niemals', 'nirgendwohin', 'nie']
    negation = 1
    for token in sentence:
        if word == token:
			#uses the syntactic dependency between the words to detect which word is negated (token.children, are the dependend words of token)
            children = [stemmer.stem(child.text) for child in token.children]
            if any(neg_word in children for neg_word in neg_words):
                negation = -1
    
    return negation
	

#example
nlp = spacy.load('de')
doc1 = nlp('Der Apfel ist nicht gut.')
doc2 = nlp('Ich habe keine Angst.')
#print(check_for_negation(doc1, doc1[4]))
#print(check_for_negation(doc2, doc2[3]))
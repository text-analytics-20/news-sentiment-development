import spacy
from nltk.stem.snowball import SnowballStemmer

stemmer = SnowballStemmer(language='german')
nlp = spacy.load('de')
neg_words = ['nicht', 'kein', 'nirgends', 'nirgendwo', 'niemand', 'niemals', 'nirgendwohin', 'nie']

#More information: https://spacy.io/usage/linguistic-features


def check_for_negated_sentence(sentence):
    # checks if whole sentence is negated (= the main verb is negated); sentence already tokenized!
    # returns sign (+1: not negated, -1: negated)
    negation = 1
    root = [token for token in sentence if token.dep_ == "ROOT"] #the main verb of the sentence
    
    if len(root) == 1:
    	# uses the syntactic dependency between the words to detect if root is negated (token.children are the dependend words of token)
    	children= [stemmer.stem(child.text) for child in root[0].children]
    	if any(neg_word in children for neg_word in neg_words):
    		negation = -1
    		
    return negation
    		

def check_for_negation(sentence, word):
    # checks if word in sentence is negated; BOTH (word and sentence) are already tokenized!
    # returns sign (+1: not negated, -1: negated)

    # TODO: handle case when word appears twice in the sentence

    negation = check_for_negated_sentence(sentence)
    	
    for token in sentence:

        if word == token:

            # uses the syntactic dependency between the words to detect which word is negated (token.children are the dependend words of token)
            children = [stemmer.stem(child.text) for child in token.children]
            
            if any(neg_word in children for neg_word in neg_words):
                negation = negation* (-1)
            	   
    return negation


# example
if __name__ == "__main__":
    doc1 = nlp('Flüchtlinge sind böse')
    doc2 = nlp('Flüchtlinge sind nicht böse')

    print(check_for_negation(doc1, doc1[2]))
    print(check_for_negation(doc2, doc2[3]))
    
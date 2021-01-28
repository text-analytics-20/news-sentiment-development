import pandas as pd
import spacy
import regex as re
from gensim.models.phrases import Phrases, Phraser
import multiprocessing
from gensim.models import Word2Vec
from time import time
import logging  # Setting up the loggings to monitor gensim
logging.basicConfig(format="%(levelname)s - %(asctime)s: %(message)s", datefmt= '%H:%M:%S', level=logging.INFO)

def hash(astring):
    return ord(astring[0])

class SentiW2v:
    def __init__(self):
        self.w2v_model = Word2Vec(min_count=20,
                            window=2,
                            size=300,
                            sample=6e-5,
                            alpha=0.03,
                            min_alpha=0.0007,
                            negative=20,
                            workers=multiprocessing.cpu_count()-1)
        self.nlp = spacy.load("de", disable=["tagger", "parser","ner"])

    def cleaning(self,doc):
        # lemma of all stop words 
        
        txt=[token.lemma_ for token in doc if not token.is_stop]
        # if sentence has more than 3 words
        if len(txt)>2:
            return ' '.join(txt)

    def train(self,path):
        df = pd.read_json(path, orient='index')        
        df = df[["date","og","text"]]
        # cleaning using regex
        brief_cleaning = (re.sub("[^A-Za-züäöÜÄÖß']",' ', str(row)).lower() for row in df["text"])
        
        t=time()
        txt= [self.cleaning(doc) for doc in self.nlp.pipe(brief_cleaning, batch_size=5000,n_threads=-1)]
        print('Time to clean up everything: {} mins'.format(round((time() - t) / 60, 2)))

        df_clean = pd.DataFrame({'clean': txt})
        df_clean = df_clean.dropna().drop_duplicates()
    
        sent = [row.split() for row in df_clean["clean"]]

        phrases = Phrases(sent, min_count=30, progress_per=10000)

        bigram = Phraser(phrases)
        sentences = bigram[sent]

        # most frequent words

        word_freq = {}
        for sent in sentences:
            for i in sent:
                if i in word_freq:
                    word_freq[i]+=1
                else:
                    word_freq[i]=1
        #print(len(word_freq))
        #sorted(word_freq, key=word_freq.get, reverse=True)[:10]
        t = time()
        self.w2v_model.build_vocab(sentences, progress_per=10000)
        print('Time to build vocab: {} mins'.format(round((time() - t) / 60, 2)))

        t = time()
        self.w2v_model.train(sentences, total_examples=self.w2v_model.corpus_count, 
                    epochs=30, report_delay=1)
        print('Time to train the model: {} mins'.format(round((time() - t) / 60, 2)))

        self.w2v_model.init_sims(replace=True) # called when finished training for memory efficiency

    def print_most_similar(self, word):
        try:
            print(sw.w2v_model.wv.most_similar(word))
        except KeyError:
            print(f"The word {word} is not in the in vocabulary.")

sw=SentiW2v()
sw.train("../data/relevant_articles.json")

sw.print_most_similar("flüchtling")
sw.print_most_similar("grenze")
sw.print_most_similar("Abschiebung")
        
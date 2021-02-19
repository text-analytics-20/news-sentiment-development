#!/usr/bin/env python3

"""
Proof of concept code for filtering an article collection (obtained from
running scraping/scrape.py) by relevant search keywords.
Prints the source URLs of articles that are recognized as relevant for our
project.
"""

import json
import os
import random
from tqdm import tqdm


def is_topic_relevant(article, keywords: list = ['migra', 'flücht', 'asyl']):
    """decides whether an article is topic relevant or not"""
    try:
        search_corpus = article['news_keywords'].lower() # not every article has the attribute news_keywords
    except KeyError:
        search_corpus = article['title'].lower() + article['text'].lower() # article['description'] could be considered as well if attribute available
    except AttributeError:
        print(f"ERROR: News Keywords are {article['news_keywords']}")
        return False
    try: 
        article['date']
    except KeyError:
        return False
    # returns True if keyword is found and false otherwise
    if any(keyword in search_corpus for keyword in keywords):
        return True 
    else:
        return False

""" def select_single_article(article,listSelectedArticles):
    ''' Calls is_topic_relevant() checks if a timestamp is available for
    input article.
    Appends relevant articles to a given list of selected articles
    returns the list to enable recursive usage'''

    # check if there is a timestamp and a news outlett name
    try: 
        articles[url]['date']
        articles[url]["og"]["site_name"]
    except KeyError:
        return
    
    # check topic relevance
    if is_topic_relevant(article):
            listSelectedArticles.append(url)
    return listSelectedArticles
"""


def write_relevant_content_to_file(file_list, relevant_articles_base, search_keywords, 
                                   new=False, training_size: int=1000, 
                                   output_after=5000, seed=0):
    if new:
        try:
            os.remove(relevant_articles_base+"_evaluation.json")
            os.remove(relevant_articles_base+"_training.json")
        except FileNotFoundError:
            print("file does already not exist")

    print(f"Start selecting files. Number of files: {len(file_list)}")
    new_cont = {}
    for json_file in tqdm(file_list):
       
        with open(json_file, "r") as jf:
            content = json.load(jf)
            if(is_topic_relevant(content)):
                new_cont[json_file] = content
    
    # seperate the files used for annotation and then training of the BERT Model
    # 1. seed the random number generator for reproducable results
    random.seed(seed)

    # 2. sample the right number of keys
    training_keys = random.sample(list(new_cont), training_size)

    # 3. create the train and evaluation dataset
    train = {k: new_cont[k] for k in new_cont if k in training_keys}
    eval = {k: new_cont[k] for k in new_cont if k not in training_keys}

    # 4. split the training set in three for annotation
    list_train = list(train)
    ann_martin = {k: train[k] for k in list_train[: len(list_train)//3]}
    ann_josephine = {k: train[k] for k in list_train[len(list_train)//3: 2*len(list_train)//3]}
    ann_simon = {k: train[k] for k in list_train[2*len(list_train)//3: ]}

    # save the data to files
    try:
        with open(relevant_articles_base+"_evaluation.json", "r+") as ra:
            content_ra = json.load(ra)
            content_ra.update(eval)
            ra.seek(0)
            json.dump(content_ra, ra)
        with open(relevant_articles_base+"_annotation_simon.json", "r+") as ra:
            content_ra = json.load(ra)
            content_ra.update(ann_simon)
            ra.seek(0)
            json.dump(content_ra, ra)
        with open(relevant_articles_base+"_annotation_josephine.json", "r+") as ra:
            content_ra = json.load(ra)
            content_ra.update(ann_josephine)
            ra.seek(0)
            json.dump(content_ra, ra)
        with open(relevant_articles_base+"_annotation_martin.json", "r+") as ra:
            content_ra = json.load(ra)
            content_ra.update(ann_martin)
            ra.seek(0)
            json.dump(content_ra, ra)
    except FileNotFoundError:
        # happens if new is enabled or function called the first time for a filepath
        with open(relevant_articles_base+"_evaluation.json", "w") as raf:
            json.dump(eval, raf)
        with open(relevant_articles_base+"_annotation_simon.json", "w") as raf:
            json.dump(ann_simon, raf)
        with open(relevant_articles_base+"_annotation_josephine.json", "w") as raf:
            json.dump(ann_josephine, raf)
        with open(relevant_articles_base+"_annotation_martin.json", "w") as raf:
            json.dump(ann_martin, raf)
    print(f"All files are written.")


def select_articles(articles):
    """Calls is_topic_relevant() and checks if a timestamp is available for
    each input article.
    Returns a list of selected relevant articles"""
    selected_articles = []
    for url in articles.keys():
        # check if there is a timestamp and a news outlett name
        try: 
            articles[url]['date']
            articles[url]["og"]["site_name"]
        except KeyError:
            continue
            
        # check topic relevance
        if is_topic_relevant(articles[url]):
            selected_articles.append(url)
    return selected_articles


if __name__ == "__main__":
    
    selected_articles = []
    data_path = 'sentiment_analysis/data/focus.json'
    
    with open(data_path, 'r') as f:
        articles = json.load(f)
        selected_articles = select_articles(articles)

    for url in selected_articles:
        # print(articles[url].keys())
        print(articles[url]["og"]["site_name"])

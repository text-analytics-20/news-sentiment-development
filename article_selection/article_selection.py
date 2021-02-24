#!/usr/bin/env python3

"""
Code for filtering an article collection (obtained from
running scraping/scrape.py) by relevant search keywords.
"""

import json
import os
import random
from tqdm import tqdm


def is_topic_relevant(article, keywords: list = ['migra', 'flücht', 'asyl']):
    """decides whether an article is topic relevant or not"""
    if not isinstance(article,dict):
        raise TypeError("article must be a dictionary")
    if not keywords or not isinstance(keywords, list) or not all(isinstance(kw,str) for kw in keywords) :
        raise TypeError("keywords must be non empty list of strings")
    
    try:
        search_corpus = article['news_keywords'].lower() # not every article has the attribute news_keywords
    except KeyError:
        try:
            search_corpus = article['title'].lower() + article['text'].lower() # article['description'] could be considered as well if attribute available
        except KeyError:
            # File has different structur than the used article files 
            return False
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


def write_relevant_content_to_file(file_list, relevant_articles_base, search_keywords, 
                                   new=False, annotation=False,
                                   training_size: int = 1000, 
                                   seed=0):
    """
    opens all files and saves them to a collectiv json if they are topic relevant
    additionaly data for annotation can be seperated
    """

    if new:
        # if file already exists remove it
        try:
            os.remove(relevant_articles_base+"_evaluation.json")
            os.remove(relevant_articles_base+"_training.json")
        except FileNotFoundError:
            pass

    print(f"Start selecting files. Number of files: {len(file_list)}")
    print(f"Keywords used for selection are: {search_keywords}")
    new_cont = {}
    for json_file in tqdm(file_list):
        try:
            with open(json_file, "r") as jf:
                content = json.load(jf)
                if(is_topic_relevant(content)):
                    new_cont[json_file] = content
        except FileNotFoundError:
            pass
    
    print(f"Total number of relavant articles: {len(new_cont)}")
    if annotation:
        print(f"Size of training set: {training_size}")
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
        ann_simon = {k: train[k] for k in list_train[2*len(list_train)//3:]}
        print(f"    -> {len(ann_martin)} articles per annotation file")
    else:
        eval = new_cont

    # save the data to files
    try:
        with open(relevant_articles_base+"_evaluation.json", "r+") as ra:
            content_ra = json.load(ra)
            content_ra.update(eval)
            ra.seek(0)
            json.dump(content_ra, ra)
        if annotation:
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
        if annotation:
            with open(relevant_articles_base+"_annotation_simon.json", "w") as raf:
                json.dump(ann_simon, raf)
            with open(relevant_articles_base+"_annotation_josephine.json", "w") as raf:
                json.dump(ann_josephine, raf)
            with open(relevant_articles_base+"_annotation_martin.json", "w") as raf:
                json.dump(ann_martin, raf)
    print(f"All files are written.")

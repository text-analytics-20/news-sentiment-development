#!/usr/bin/env python3.8

"""
Prototype for a pipeline. It is contoled by a config.ini file 
and calles the functions for preprocessing and analysis. 
"""

import configparser
import glob
from sentiment_analysis.word2vec_sentiment import *
import sentiment_analysis.sentimentDictionary as sd
#from sentiment_analysis.fuctionality_sentiment_analysis import analyse_sentiment, listSearchTerm
from sentiment_analysis.bert import GSBertPolarityModel
import article_selection.article_selection as article_selection
import json
import sys
import os
from time import time
from tqdm import tqdm
from typing import Sequence
import traceback
import pandas as pd


def calulate_sentiment(input_path: str, output_path: str, search_words: list, methods: Sequence[str]):
    # Initialize BERT models
    generic_sentibert, finetuned_sentibert = None, None
    if 'generic_sentibert' in methods:
        generic_sentibert = GSBertPolarityModel("oliverguhr/german-sentiment-bert")
    if 'finetuned_sentibert' in methods:
        raise NotImplementedError  # TODO
        finetuned_sentibert = GSBertPolarityModel('path-to-model')
    
    # get the data from the given file path 
    content = pd.read_json(input_path, orient="index")
    content = content[["date", "text", "url", "title"]]
    content = content.sample(20)
    # create dictionary with output data
    data = {}

    list_len = len(content["text"])
    print("Start calculating sentiment")
    print(f"Total number of articles is: {list_len}")
    for p, row in tqdm(content.iterrows(), total=list_len, dynamic_ncols=True):

        # use only articles that have all needed information
        try:
            text = row['text']
            publisher = row["url"].split("//")[1].split("/")[0].split(".")[1]
            date = row['date']
            title = row['title']
            url = row['url']
        except KeyError:
            traceback.print_exc()
            continue

        # initialize the output data
        data[url] = {
            'publisher': publisher,
            'date': date,
            'title': title,
            'text': text
        }
        # add a key : value pair for all sentiment methods specified in the config 

        # 1. use the sentiment dictionary "sentiws"
        if 'sentiws' in methods:
            sentiment_sentiws = sd.analyse_sentiment(text, search_words)
            if sentiment_sentiws == '':
                sentiment_sentiws = float('nan')
            else:
                sentiment_sentiws = float(sentiment_sentiws)
            data[url]['sentiment_sentiws'] = sentiment_sentiws

        # 2. use the generic bert model
        if 'generic_sentibert' in methods:
            sentiment_generic_sentibert = generic_sentibert.analyse_sentiment(text)
            data[url]['sentiment_generic_sentibert'] = sentiment_generic_sentibert
            
        # 3. use the self traind bert model
        if 'finetuned_sentibert' in methods:
            raise NotImplementedError  # TODO
            sentiment_finetuned_sentibert = finetuned_sentibert.analyse_sentiment(text)
            data[url]['sentiment_finetuned_sentibert'] = sentiment_finetuned_sentibert

    # write data to file
    with open(output_path, "w", encoding='utf-8') as f:
        print(f"Write data to {output_path}")
        json.dump(data, f, default=str, ensure_ascii=False)


if __name__ == "__main__":

    # read config file
    try:
        config_file = sys.argv[1]
        config = configparser.ConfigParser()
        config.read(config_file)
    except IndexError:
        print("Error: Supply a config.ini file") 
        quit()
    
    # ==============================
    # Selection of relevant Articles
    # ==============================
    if config.getboolean("ArticleSelection","run_article_selection"):
        
        # create input filepath for article selection from:
        # the path to the folders and the start and end year
        base_path = config.get("ArticleSelection", "input_path_base")
        start_year = config.getint("ArticleSelection", "start_year")
        end_year = config.getint("ArticleSelection", "end_year")
        data_path_list = [base_path+str(year)+"/" for year in range(start_year, end_year+1)]
        # create list of all data paths
        json_file_list = []
        for path in data_path_list:
            json_file_list += [file_path for file_path in glob.glob(path+"*.json")]

        # get keywords, output_path
        search_keywords = config.get("ArticleSelection", "search_words").lower().split(", ")
        output_base = config.get("ArticleSelection", "output_base")
        
        # create new file or append to existing file
        create_new_files = not config.getboolean("ArticleSelection", "append_to_existing_file")

        # if annotation files are needed get training_size and seed 
        use_annotation = config.getboolean("ArticleSelection", "use_annotation")
        training_size = config.getint("ArticleSelection", "training_size")
        seed = config.getint("ArticleSelection", "seed")
     
        # open all files containing an article 
        # check if the topic is relevannt
        # if use_anotation is True output is split in four files: 
        #   1. evaluation (size_all-training_size)
        #   2. 3 annotation files with the names of the annotators 1/3 training_size
        article_selection.write_relevant_content_to_file(json_file_list, 
                                                         output_base, 
                                                         search_keywords=search_keywords,
                                                         new=create_new_files,
                                                         training_size=training_size,
                                                         seed=seed, 
                                                         annotation=use_annotation)
    
    # ===================
    # Word2Vec analysis
    # ===================
    if config.getboolean("Analysis", "run_w2v"): 
        input_file = config.get("Analysis", "input_file") 
        search_words = config.get("Analysis", "search_words_w2v").lower().split(",")
        base_output_path = config.get("Analysis", "output_base_w2v")
        start_year = config.getint("Analysis", "start_year")
        end_year = config.getint("Analysis", "end_year")

        # all articles of the same year are one dataset
        if config.getboolean("Analysis","run_by_year"):
            similarity_by_year(input_file, base_output_path, search_words,
                               start_year, end_year)

        # all articles of the same publisher are one dataset
        if config.getboolean("Analysis","run_by_publisher"):
            similarity_by_publisher(input_file, base_output_path, search_words,
                                    start_year, end_year)

        # all articles of the same publisher during the same year are one dataset
        if config.getboolean("Analysis","run_by_publisher_by_year"):
            similarity_by_year_and_publisher(input_file, base_output_path,
                                             search_words, start_year, 
                                             end_year)
    
    # ==================
    # Sentiment analysis
    # ==================
    if config.getboolean("Analysis", "run_senti"):
        input_file = config.get("Analysis", "input_file") 
        search_words = config.get("Analysis", "search_words").lower().split(",")
        output_file = config.get("Analysis", "output_senti")
        methods = config.get('Analysis', 'senti_methods').lower().split(", ")
        
        # calculate the article sentiment
        # using one or multiple of the following methods:
        #   1. Sentiment-Dictionary (sentiws)
        #   2. Neuronal-Network based Bert model
        #      trained for gerneral sentiment analysis
        #   3. Same Bert model with additional training
        #      using labeled parts of news-articles about refugees
        calulate_sentiment(input_file, output_file,
                           search_words, methods=methods)

                        
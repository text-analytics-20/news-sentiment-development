#!/usr/bin/env python3.8

"""
Prototype for a pipeline. It is contoled by a config.ini file and calles the functions for preprocessing and analysis. 
"""

import configparser
import glob
from sentiment_analysis.word2vec_sentiment import *
import sentiment_analysis.sentimentDictionary as sd
#from sentiment_analysis.fuctionality_sentiment_analysis import analyse_sentiment, listSearchTerm
import article_selection.article_selection as article_selection
import json
import sys
import os
from time import time
from tqdm import tqdm
import traceback

def calulate_sentiment(input_path: str, output_path: str, search_words: list, type: str = "DIC"):
    content = pd.read_json(input_path, orient="index")
    content = content[["date","og","text","url"]]
    data = {}
    # counter=1
    output_after = 200
    t = time()
    list_len = len(content["text"])
    print("Start calculating Sentiment with sentiws")
    print(f"Total number of articles is: {list_len}")
    for i , row in tqdm(content.iterrows()):
        # if counter%output_after==0:
        #     print(f"{counter} of the files are read. {round(float(counter)/list_len*100 , 1)}% Time since start: {round((time() - t) / 60, 2)} min")
        #     print(f"Approximate time till end is: {round((list_len/float(counter) * (time() - t)-(time() - t)) / 60 , 2)} min") 
        # counter+=1
        try: 
            text = row['text']
            publisher = row["url"].split("//")[1].split("/")[0].split(".")[1]
            date = row['date']
            title = row['title']
        except KeyError:
            traceback.print_exc()
            return
        # textSentiment = None
        if type=="DIC":
            textSentiment = sd.analyse_sentiment(text, search_words)
        if type=="BERT":
            print("something")
            # textSentiment = sd.analyse_sentiment(text, search_words)
        if textSentiment != "":
            data[i] = [publisher, date, textSentiment, title, text]
            # data = f"{publisher}, {date}, {textSentiment}, {article_path}\n"
    with open(output_path, "w") as dataFile:
            json.dump(dataFile, data)


if __name__ == "__main__":

    config_file = sys.argv[1]
    config = configparser.ConfigParser()
    config.read(config_file)

    # ==============================
    # Selection of relevant Articles
    # ==============================
    if config.getboolean("ArticleSelection","run_article_selection"):
        # create input filepath for article selection
        base_path = config.get("ArticleSelection", "input_path_base")
        output_base = config.get("ArticleSelection", "output_base")
        start_year = config.getint("ArticleSelection", "start_year")
        end_year = config.getint("ArticleSelection", "end_year")
        data_path_list = [base_path+str(year)+"/" for year in range(start_year, end_year+1)]
        training_size = config.getint("ArticleSelection", "training_size")
        search_keywords = config.get("ArticleSelection", "search_words").lower().split(",")
        seed = config.getint("ArticleSelection", "seed")
        # create list of all data paths
        json_file_list = []
        for path in data_path_list:
            json_file_list +=  [file_path for file_path in glob.glob(path+"*.json")]
        
        # open all files containing an article 
        # check if the topic is relevannt
        # output is split in four files: 
        #   1. evaluation (size_all-training_size)
        #   2. 3 annotation files with the names of the annotators 1/3 training_size
        article_selection.write_relevant_content_to_file(json_file_list, output_base, 
                                                         search_keywords=search_keywords,
                                                         new=True, training_size=training_size
                                                         , seed=seed)
    
    # ===================
    # Word2Vec analysis
    # ===================
    if config.getboolean("Analysis","run_w2v"): 
        input_file = config.get("Analysis","input_file") 
        search_words = config.get("Analysis","search_words").lower().split(",")
        base_output_path = config.get("Analysis","output_base_w2v")
        start_year = config.getint("Analysis","start_year")
        end_year = config.getint("Analysis","end_year")
        if config.getboolean("Analysis","run_by_year"):
            similarity_by_year(input_file, base_output_path, search_words, start_year, end_year)
        if config.getboolean("Analysis","run_by_publisher"):
            similarity_by_publisher(input_file, base_output_path ,search_words, start_year, end_year)
        if config.getboolean("Analysis","run_by_publisher_by_year"):
            similarity_by_year_and_publisher(input_file, base_output_path ,search_words, start_year, end_year)
    
    # ==============================
    # Sentiment Dictionary-Apporach
    # ==============================
    if config.getboolean("Analysis", "run_sentiws"):
        input_file = config.get("Analysis","input_file") 
        search_words = config.get("Analysis","search_words").lower().split(",")
        output_file=config.get("Analysis","output_sentiws")
        calulate_sentiment(input_file,output_file,search_words)
        # start_year = config.get("Analysis","start_year")
        # end_year = config.get("Analysis","end_year")

#TO DO:
# want to check for doubles for this use same sentiDic entity for all articles   
# this also gives the opportunity to use the saved sentences of all articles for creation of a word-cloud  
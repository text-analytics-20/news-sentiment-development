#!/usr/bin/env python3.8

"""
Prototype for a pipeline. It is controlled by a config.ini file
and calls the functions for preprocessing and analysis.
"""

import configparser
import glob
import sys

import article_selection.article_selection as article_selection
from sentiment_analysis.inference import calulate_sentiment, eval_sentiment
from sentiment_analysis.word2vec_sentiment import *
from visualization.dash_plot import dash_plot

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
    if config.getboolean("ArticleSelection", "run_article_selection"):

        # create input filepath for article selection from:
        # the path to the folders and the start and end year
        base_path = config.get("ArticleSelection", "input_path_base")
        start_year = config.getint("ArticleSelection", "start_year")
        end_year = config.getint("ArticleSelection", "end_year")
        data_path_list = [base_path + str(year) + "/" for year in range(start_year, end_year + 1)]
        # create list of all data paths
        json_file_list = []
        for path in data_path_list:
            json_file_list += [file_path for file_path in glob.glob(path + "*.json")]

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
        if config.getboolean("Analysis", "run_by_year"):
            similarity_by_year(input_file, base_output_path, search_words,
                               start_year, end_year)

        # all articles of the same publisher are one dataset
        if config.getboolean("Analysis", "run_by_publisher"):
            similarity_by_publisher(input_file, base_output_path, search_words,
                                    start_year, end_year)

        # all articles of the same publisher during the same year are one dataset
        if config.getboolean("Analysis", "run_by_publisher_by_year"):
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
        finetuned_sentibert_path = config.get('Analysis', 'finetuned_sentibert_path')

        # calculate the article sentiment
        # using one or multiple of the following methods:
        #   1. Sentiment-Dictionary (sentiws)
        #   2. Neuronal-Network based Bert model
        #      trained for gerneral sentiment analysis
        #   3. Same Bert model with additional training
        #      using labeled parts of news-articles about refugees
        calulate_sentiment(
            input_file,
            output_file,
            search_words,
            methods=methods,
            finetuned_sentibert_path=finetuned_sentibert_path
        )

    # =============================
    # Sentiment analysis evaluation
    # =============================
    if config.getboolean("Analysis", "run_senti_eval"):
        senti_eval_input = config.get("Analysis", "senti_eval_input")
        search_words = config.get("Analysis", "search_words").lower().split(",")
        senti_eval_output = config.get("Analysis", "senti_eval_output")
        methods = config.get('Analysis', 'senti_methods').lower().split(", ")
        finetuned_sentibert_path = config.get('Analysis', 'finetuned_sentibert_path')

        # Perform quantitative evaluation of sentiment analysis approaches
        # using one or multiple of the following methods:
        #   1. Sentiment-Dictionary (sentiws)
        #   2. Neuronal-Network based Bert model
        #      trained for gerneral sentiment analysis
        #   3. Same Bert model with additional training
        #      using labeled parts of news-articles about refugees
        eval_sentiment(
            senti_eval_input,
            senti_eval_output,
            search_words,
            methods=methods,
            finetuned_sentibert_path=finetuned_sentibert_path
        )

    # ==================
    # Plotting
    # ==================
    if config.getboolean("Plotting", "sentiment_plot"):
        input_file = config.get("Plotting", "input_file")
        dash_plot(input_file)

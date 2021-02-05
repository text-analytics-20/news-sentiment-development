import configparser
import glob
from sentiment_analysis.word2vec_sentiment import *
#from sentiment_analysis.sentimentDictionary import sentimentDictionary
#from sentiment_analysis.fuctionality_sentiment_analysis import analyse_sentiment, listSearchTerm
import article_selection.article_selection as artSel
import json
import sys
import os
from time import time

def calulate_sentiment(content, save_path, article_path):
    try: 
        text = content['text']
        site_name = content["og"]["site_name"] #überprüfen
    except KeyError:
        return
    textSentiment = analyse_sentiment(text, listSearchTerm)
    if textSentiment != 0:
        data = f"{site_name}, {textSentiment}, {article_path}\n"
        with open(save_path, "a") as dataFile:
            dataFile.write(data)

def write_relevant_content_to_file(file_list, relevant_articles_file, new=False, output_after=5000):
    if new:
        try:
            os.remove(relevant_articles_file)
        except FileNotFoundError:
            print("file does already not exist")
    t=time()
    print(f"Start selecting files. Number of files: {len(file_list)}")
    counter=0
    new_cont={}
    for json_file in file_list:
        if counter%output_after==0 and counter>0:
            print(f"{counter} of the files is read. {round(float(counter)/len(file_list)*100 , 0)}% Time since start: {round((time() - t) / 60, 2)} min")
            print(f"Approximate time till end is: {round((len(file_list)/float(counter) * (time() - t)-(time() - t)) / 60 , 2)} min") 
        counter+=1
        with open(json_file ,"r") as jf:
            content=json.load(jf)
            if(artSel.is_topic_relevant(content)):
                new_cont[json_file]=content
    try:    
        with open(relevant_articles_file ,"r+") as ra:
            content_ra = json.load(ra)
            content_ra.update(new_cont)
            ra.seek(0)
            json.dump(content_ra,ra)
    except FileNotFoundError:
        # happens if new is enabled or function called the first time for a filepath
        with open(relevant_articles_file ,"w") as raf:
            json.dump(new_cont,raf)
    print(f"All files is read. Time since start: {round((time() - t) / 60, 2)}")


if __name__ == "__main__":

    config_file = sys.argv[1]
    config = configparser.ConfigParser()		
    config.read(config_file) 

    # ==============================
    # Selection of relevant Articles
    # ==============================
    if config.getboolean("ArticleSelection","run_article_selection"):
        #create input filepath for article selection
        base_path=config.get("ArticleSelection","input_path_base")
        start_year=config.getint("ArticleSelection","start_year")
        end_year=config.getint("ArticleSelection","end_year")
        data_path_list = [base_path+str(year)+"/" for year in range(start_year,end_year+1)]
            
        # create list of all data paths
        json_file_list = []
        for path in data_path_list:
            json_file_list +=  [file_path for file_path in glob.glob(path+"*.json")]
        
        # open all files containing an article and if the topic is relevannt save it to a collectiv json file 
        write_relevant_content_to_file(json_file_list, config.get("ArticleSelection","output_file") ,True)
    
    # ===================
    # Word2Vec analysis
    # ===================
    if config.getboolean("Analysis","run_w2v"): 
        input_file = config.get("Analysis","input_file") 
        search_words = config.get("Analysis","search_words").lower().split(",")
        base_output_path=config.get("Analysis","output_base_w2v")
        start_year = config.get("Analysis","start_year")
        end_year = config.get("Analysis","end_year")
        print(input_file)
        if config.getboolean("Analysis","run_by_year"):
            similarity_by_year(input_file, base_output_path ,search_words, start_year, end_year)
        if config.getboolean("Analysis","run_by_publisher"):
            similarity_by_publisher(input_file, base_output_path ,search_words, start_year, end_year)
        if config.getboolean("Analysis","run_by_publisher_by_year"):
            similarity_by_year_and_publisher(input_file, base_output_path ,search_words, start_year, end_year)

#TO DO:
# want to check for doubles for this use same sentiDic entity for all articles   
# this also gives the opportunity to use the saved sentences of all articles for creation of a word-cloud  
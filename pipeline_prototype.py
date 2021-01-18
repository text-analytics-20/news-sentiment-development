import glob 
from sentiment_analysis.sentimentDictionary import sentimentDictionary
from sentiment_analysis.fuctionality_sentiment_analysis import analyse_sentiment, listSearchTerm
import article_selection.article_selection as artSel
import json

def calulate_sentiment(content, save_path, article_path):
    try: 
        text = content['text']
        site_name = content["og"]["site_name"]
    except KeyError:
        return
    textSentiment = analyse_sentiment(text, listSearchTerm)
    if textSentiment != 0:
        data = f"{site_name}, {textSentiment}, {article_path}\n"
        with open(save_path, "a") as dataFile:
            dataFile.write(data)

if __name__ == "__main__":
    data_path_list = ["data/ta_scrape100k_2007/","data/ta_scrape100k_2008/","data/ta_scrape100k_2009/"]
    save_path = "data/sentiment.csv"
    jason_file_list = []

    # create list of all data paths
    for path in data_path_list:
        jason_file_list +=  [file_path for file_path in glob.glob(path+"*.json")]

    # open all files containing on article and if the topic is relevannt calculate their content
    for json_file in jason_file_list:
        with open(json_file ,"r") as jf:
            content=json.load(jf)
            if(artSel.is_topic_relevant(content)):
                calulate_sentiment(content, save_path, json_file)
    #print(publishers)
#TO DO:
# want to check for doubles for this use same sentiDic entity for all articles   
# this also gives the opportunity to use the saved sentences of all articles for creation of a word-cloud  
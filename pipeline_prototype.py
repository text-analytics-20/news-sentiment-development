import glob 
#from sentiment_analysis.sentimentDictionary import sentimentDictionary
#from sentiment_analysis.fuctionality_sentiment_analysis import analyse_sentiment, listSearchTerm
import article_selection.article_selection as artSel
import json
import os

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

def write_relevant_content_to_file(file_list, relevant_articles_file, new=False):
    if new:
        try:
            os.remove(relevant_articles_file)
        except FileNotFoundError:
            print("file does already not exist")
    for json_file in jason_file_list:
        with open(json_file ,"r") as jf:
            content=json.load(jf)
            if(artSel.is_topic_relevant(content)):
                new_cont = {json_file : content}
                try:    
                    with open(relevant_articles_file ,"r+") as ra:
                        content_ra = json.load(ra)
                        content_ra.update(new_cont)
                        ra.seek(0)
                        json.dump(content_ra,ra)
                except FileNotFoundError:
                    with open(relevant_articles_file ,"w") as raf:
                        json.dump(new_cont,raf)


if __name__ == "__main__":
    data_path_list = ["data/ta_scrape100k_2007/","data/ta_scrape100k_2008/","data/ta_scrape100k_2009/"]
    relevant_articles = "data/relevant_articles.json"
    save_path = "data/sentiment.csv"
    if True:
        # create list of all data paths
        jason_file_list = []
        for path in data_path_list:
            jason_file_list +=  [file_path for file_path in glob.glob(path+"*.json")]
        
        # open all files containing an article and if the topic is relevannt save it to a collectiv json file 
        write_relevant_content_to_file(jason_file_list, relevant_articles,True)

    if True: 
        with open(relevant_articles,"r") as f:
            content = json.load(f)
            i=0
            for k in content:
                if i>10:
                    break 
                i+=1
                print(k["date"])
    
    
    #calulate_sentiment(content, save_path, json_file)
    #print(publishers)
#TO DO:
# want to check for doubles for this use same sentiDic entity for all articles   
# this also gives the opportunity to use the saved sentences of all articles for creation of a word-cloud  
#!/usr/bin/env python3

"""
Proof of concept code for filtering an article collection (obtained from
running scraping/scrape.py) by relevant search keywords.
Prints the source URLs of articles that are recognized as relevant for our
project.
"""

import json


def is_topic_relevant(article):
    """decides whether an article is topic relevant or not"""
    keywords = ['migra', 'flücht', 'asyl']
    try:
        search_corpus = article['news_keywords'].lower() # not every article has the attribute news_keywords
    except KeyError:
        search_corpus = article['title'].lower() + article['text'].lower() # article['description'] could be considered as well if attribute available

    # returns True if keyword is found and false otherwise
    if any(keyword in search_corpus for keyword in keywords):
        return True 
    else:
        return False

"""def select_single_article(article,listSelectedArticles):
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
    data_path='sentiment_analysis/data/focus.json'
    
    with open(data_path, 'r') as f:
        articles = json.load(f)
        selected_articles = select_articles(articles)

    for url in selected_articles:
        #print(articles[url].keys())
        print(articles[url]["og"]["site_name"])

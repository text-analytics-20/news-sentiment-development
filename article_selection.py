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


def select_articles(articles):
    """Calls is_topic_relevant() and checks if a timestamp is available for
    each input article.
    Returns a list of selected relevant articles"""
    selected_articles = []
    for url in articles.keys():
        
        # check if there is a timestamp
        try: 
            articles[url]['date']
        except KeyError:
            continue
            
        # check topic relevance
        if is_topic_relevant(articles[url]):
            selected_articles.append(url)
    return selected_articles
	
	
selected_articles = []
with open('test_data/spiegel.json', 'r') as f:
    articles = json.load(f)
    selected_articles = select_articles(articles)

for url in selected_articles:
    print(url)

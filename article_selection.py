#function which decides whether an article is topic relevant or not
def is_topic_relevant(url):
    keywords = ['migra', 'flücht', 'asyl']
    try:
        search_corpus = url['news_keywords'].lower() #not every article has the attribute news_keywords

    except KeyError:
        search_corpus = url['title'].lower() + url['text'].lower() #url['description'] could be considered as well if attribute available
    
    #returns true if keyword is found and false otherwise
    if any(keyword in search_corpus for keyword in keywords):
        return True 
    else:
        return False

#calls function is_topic_relevant and checks if a timestamp is available for each input article
#returns list of selcted relevant articles
def select_articles(articles):
    selected_articles = []
    for url in articles.keys():
        
        #check if there is a timestamp
        try: 
            articles[url]['date']
        except KeyError:
            continue
            
        #check topic relevance
        if is_topic_relevant(articles[url]):
            selected_articles.append(url)
            
    return selected_articles
	
	
import json
selected_articles = []
with open('spiegel.json', 'r') as f:
    articles = json.load(f)
    selected_articles = select_articles(articles)

#print(selected_articles)
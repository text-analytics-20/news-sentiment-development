import json
from dictionary_approach import sentimentDictionary as sentiDic 

def analyse_sentiment(text: str, searchTerm: str) -> float:
    if not searchTerm in text:
        return 0.0
    sd = sentiDic()
    sd.predict_sentiment(text, searchTerm)
    return sd.sentimentText
if __name__ == "__main__":
    with open('../test_data/spiegel.json', 'r') as f:
        articles = json.load(f)
        for url in articles:
            text=''
            try: 
                text=articles[url]['text']
            except KeyError:
                continue
            print(analyse_sentiment(text, "flüch"))



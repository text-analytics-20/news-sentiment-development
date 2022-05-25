# News sentiment development on the example of “Migration”
Analyzing the sentiment development of news articles with the topic "migration" over time.
This project was done in the course of the [Text Analytics lecture](https://dbs.ifi.uni-heidelberg.de/teaching/current/text-analytics-ita/) at Heidelberg University.

## Code structure
- **`pipeline.py`**: All main components of the project are included in the pipeline. The pipeline is controlled by the config.ini.

### Pipeline components
- **`article_selection`**: Selects articles which are relevant for the analysis by a keyword search
- **`sentiment_analysis`**: Contains the different approaches to analyze the sentiment
    - **`bert.py`**: Evaluation of sentiment by the BERT model
    - **`sentiment_dictionary.py`**: Evaluation of sentiment through the SentiWS dictionary
    - **`negation_handling.py`**: Improvement of the dictionary approach by handling the negation of words
    - **`word2vec_sentiment.py`**: Word2Vec Model to get synonyms of search words for qualitative analysis
    - **`inference.py`**: functions for applying and evaluating sentiment analysis methods on large batches of data

- **`training`**: Training code to fine-tune the BERT Model (the result of the training is published [here](https://huggingface.co/mdraw/german-news-sentiment-bert))
- **`visualization`**:
    - **`dash_plot.py`**: Dash application to show sentiment timelines
    - **`wordcloud.py`**: Generates word clouds of results from word2vec model

### Other components
- **`annotation`**: Tool to annotate articles to generate training and test data
- **`scraping`**: Generating the articles
- **`pipeline_test.py`**: code tests

## Setup Instructions:
               
### Setup requirements: Linux, Python 3.8

1. Clone this repository

2. Create a new virtual environment and activate it:
   ```
    virtualenv env
    source env/bin/activate
    ```
3. Install the dependencies from the frozen-requirements.txt and then install the german language-package for spacy:
    ```
    pip install -r frozen-requirements.txt
    python -m spacy download de
    ```

## Instructions to run the code

### Obtain the news article data dataset
Either ask us for the scraped articles or use `scraping/collect_articles.py` to build the dataset yourself (can take a few days).
For detailed instructions, refer to the docstring of [collect_articles.py](scraping/collect_articles.py).

The expected article source files (*-sources.txt files) can be obtained from https://wortschatz.uni-leipzig.de/en/download/German). They are located inside of the .tar.gz files listed there. For this project we used the following archives:

- `deu_news_2007_100k.tar.gz`
- `deu_news_2008_100k.tar.gz`
- `deu_news_2009_100k.tar.gz`
- `deu_news_2010_100k.tar.gz`
- `deu_news_2011_100k.tar.gz`
- `deu_news_2012_100k.tar.gz`
- `deu_news_2013_100k.tar.gz`
- `deu_news_2014_100k.tar.gz`
- `deu_news_2015_100k.tar.gz`
- `deu_newscrawl_2017_100k.tar.gz`
- `deu_newscrawl_2018_100k.tar.gz`
- `deu_newscrawl-public_2019_100k.tar.gz`

### Run the pipeline
The pipeline is controlled by the `config.ini` file. 
Configure it as you wish.
Then run 
```
pipeline.py config.ini
```

## Note on data availability
We cannot upload our article data publicly due to copyright reasons.
If you are interested in our dataset version and/or in the intermediate results, please email us so we can help you.
Our finetuned BERT model can be found at https://huggingface.co/mdraw/german-news-sentiment-bert


## Project report

We share a redacted version of our final project report [here](news-sentiment-report-public.pdf).
Please refer to this document for more details on the background, methods and results of the associated project for which the code was written.


## Team members
- Simon Lüdke (simon.luedke at gmx.de)
- Josephine Grau (josephine.grau at web.de)
- Martin Drawitsch (martin.drawitsch at gmail.com)


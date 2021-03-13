# News sentiment development on the example of “Migration”
Analyzing the sentiment development of news articles with the topic "migration" over time.

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

- **`training`**: Training code to fine-tune the BERT Model
- **`visualization`**:
    - **`dash_plot.py`**: Dash application to show sentiment timelines
    - **`wordcloud.py`**: Generates word clouds of results from word2vec model

### Other components
- **`annotation`**: Tool to annotate articles to generate training and test data
- **`scraping`**: Generating the articles
- **`pipeline_test.py`**: code tests

# Set-Up Instructions:
               
### Set up requirements: Linux, Python 3.8

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

# Instructions to run the code

## Obtain the news article data dataset
Either ask us for the scraped articles or use `scraping/collect_articles.py` to build the dataset yourself (can take a few days).
For detailed instructions, refer to the docstring of [collect_articles.py])https://github.com/text-analytics-20/news-sentiment-development/blob/main/scraping/collect_articles.py).
The expected article source files (*-sources.txt files) can be obtained from https://wortschatz.uni-leipzig.de/en/download/german). They are located inside of the .zip files listed there.

## Run the pipeline
The pipeline is controlled by the `config.ini` file. 
Configure it as you wish.
Then run 
```
pipeline.py config.ini
```

### We can provide already generated data on request to not violate copyrights.

Team members:
- Simon Lüdke (simon.luedke at gmx.de)
- Josephine Grau (josephine.grau at web.de)
- Martin Drawitsch (martin.drawitsch at gmail.com)


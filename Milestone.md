# News sentiment development on the example of “Migration”

Team members:

- Simon Lüdke (simon.luedke at gmx.de)
- Josephine Grau (josephine.grau at web.de)
- Martin Drawitsch (martin.drawitsch at gmail.com)

## Milestone 1

We have worked on all the basic steps which are necessary for conducting the sentiment analysis on our data. These include the scraping of articles, the selection of topic-related articles and first tries of evaluating the sentiment of newspaper articles. In the following we describe our progress, thoughts and planned future work in each of the areas that we worked on.

### Article Scraping

Our initial approach to collecting news data for our analysis is based on directly crawling public news websites for links to articles, collecting their URLs and then downloading, parsing and categorizing each article based on the collected URLs. We implemented these steps with help of the [newspaper](https://github.com/codelucas/newspaper) Python library and made use of JSON for storing each scraped article with its text and metadata (publication date, title, keywords found in HTML meta-tags etc.) in a machine-readable format for the later processing steps. 

We have implemented this part of the pipeline as a stand-alone Python script [here](https://github.com/text-analytics-20/news-sentiment-development/blob/main/scraping/scrape.py). For the our storage format specification, refer to the documentation at the top of the script.

With this code we have sucessfully scraped hundreds of articles from news websites including https://spiegel.de, https://focus.de, https://de.rt.com, https://bild.de and https://welt.de and have stored the resulting article collections in separate files, which unforunately cannot share here due to copyright reasons.

However, we found that despite our initial expectations, the [newspaper](https://github.com/codelucas/newspaper) library’s site crawling functionality only can find a very limited number of articles on each site and only finds recently published articles.
Although we could use this limited collection for testing and building the later steps of our analysis pipeline, it is of course not sufficient for our planned large-scale historical analysis.

Since we have not yet found a suitable method to automatically crawl all relevant news sources for article URLs and associated publication dates, we have therefore focused our recent efforts on using the publicly available news datasets from https://wortschatz.uni-leipzig.de/en/download/german.
The main content of these datasets consists of single sentences without their articles’ contexts, but the included “deu_news_*_-sources.txt” files do contain URLs and publication dates in most cases, starting from year 2007 (earlier years’ datasets only contain the domain information).
We plan on using just these lists of sources and dates to collect our corpus of articles, which will thus consist of articles published between 2007 and 2019. Since for each year there are at least 1 million articles from a diverse set of German-language sources in the dataset, we expect that we can build a sufficiently large collection of articles for our project.

We are currently adapting our aformentioned web scraping tool and sucessfully tested it on a small sample of old article URLs that we found in this dataset 2007, 2009) to see if the URLs are still usable.
In the coming weeks we will finalize our data collection code and try to scrape as many articles as possible from the mentioned sources.


### Definition of topic-relevant articles

A newspaper article is selected to contribute to the sentiment analysis according to certain keywords. We decided to search for words including the following substrings, as they have a rather neutral sentiment and define the topic clearly:

- "flücht"
- "migra"
- "asyl"

These include words like: Flüchtling, Flüchtlingspolitik, Flüchtlingskrise, geflüchtet, Geflüchtete(r), Migrant(in/en), Migration, Asyl, Asylpolitik, Asylverfahren, ...

Some newspaper sources already have the attribute “keywords” which will be used in this case. Otherwise at least one of the keywords must appear in either the title and the text or the article description (if this attribute is available). Both attributes “text” and “title” are available for all considered news sources.
As German newspapers focus on the migration towards Europe, articles of related, for us non-relevant content, are the exception (e.g. migration from Mexico to the United States) and neglegible.

However, there are possibilities to elaborate the search, if necessary:

- Include (only) articles which contain at least one of the following keywords in their text: EU, Griechenland, Italien, Türkei, Ungarn, Europa, Libyen, Syrien, Afghanistan, Asyl- (verfahren, politik, antrag, …), Flüchtlings- (lager, politik, route…), kontrollieren, Grenze, flüchten, kriminell/ Kriminelle, Frontex, Fremdenfeindlichkeit, retten/ Rettung, Schlauchboot, Integration, Herkunftsland, Abschiebestopp/ Abschiebung, Geflüchtete(r)
- Exclude articles Articles with the following country names in the title, description or keyword attributes are disregarded: USA, Mexiko, Japan, China, Indien

This would eliminate more “false-positive” articles, for example https://www.rnz.de/politik/politik-ausland_artikel,-heikles-thema-zuwanderung-Ueberaltertes-japan-will-sich-fuer-arbeitsmigranten-oeffnen-_arid,405788.html.
In seldom cases there are also “false-negative” articles, such as:
https://www.sueddeutsche.de/politik/seehofer-syrien-abschiebung-straftaeter-gefaehrder-1.5144871

At this point we don’t see a necessity to refine the search. False-negatives do not influence our analysis to great extent and occur very rarely. False-positives should be neglegible according to a much higher frequency of topic-related articles. A refined search would furthermore influence our sentiment analysis by the sentiment of additional keywords (e.g. “kriminell”). 
Qualitative tests for the newspaper articles of spiegel.de show that the search works sufficiently well. An adaptation is only considered if later results show different behaviour. A basic Python script which implements the search is available on our repository. 


### Sentiment analysis

Sentiment analysis for news articles is difficult because in contrast to reviews they are generally written in a more neutral style and there is not one predefined topic (see [Sentiment Analysis in the News](https://arxiv.org/pdf/1309.6202.pdf)).
 
Since we want to specifically investigate the sentiment in German news articles, we also need tools that work with the German language.
 
For a first approach we use the [spacy-ws](https://spacy.io/universe/project/spacy-sentiws) extension to spacy that is based on the [SentiWS](https://wortschatz.uni-leipzig.de/en/download) corpus of the Leipzig University which contains around 1,650 positive and 1,800 negative adjectives, adverbs, verbs and nouns as well as their inflections. The positive and negative polarity of the words is given in the range of [-1;1].
Using this, we calculate the sum of weighted words of every sentence containing a search term e.g. "flücht". The word containing the search term is naturally neglected to reduce systematic errors. "Flüchtling" for example is weighed negatively in itself.
 
At the moment this aproach has the flaw that the direction of sentiment is not clear:

 - 'Radikale Afdler versuchen sich über Hetzkampagnen gegen Flüchtlinge zu profilieren.' : -0.487
 - 'Es ist schrecklich, dass jeden Tag Flüchtlinge im Mittelmeer ertinken.' : -0.0242
 - 'Flüchtlinge nehmen unsere Arbeitsplätze weg.' : 0.0

In this example the only sentence that is against refugees (Flüchtlinge) is also the only sentence with neutral sentiment. One reason for this is 
that the verb "wegnehmen" with clear sentiment is split into two words without sentiment.
A possible solution would be to use part-of-speech tags to e.g. combine split verbs into one. If we find a way to clearly label the object and subject of a sentence it could also be possible to use this for improvements.
- The SentiWS-Corpus contains only a part of the words carrying sentiment. It is by no means complete.
- While inflictions of the words are contained, compound words can not be detected. (e.g. "Flüchtling" has a sentiment weight but "Wirtschaftsflüchtling" does  not). The solution to  this problem lies in additional preprocessing.

An other shortcoming of this approach is the possibility of false sentences. "Searching with the term "flücht" you can e.g. get the following sentence with no connection to refugees and a clear sentiment:   
- 'Im Prozess um die Terrorserie vom Januar 2015 sind 14 Menschen angeklagt - drei von ihnen sind aber flüchtig.': -0.0048

 
Another possible approach is based on https://huggingface.co/oliverguhr/german-sentiment-bert, a BERT based model for German sentiment analysis.
The problem is that this model is trained on reviews and tweets for positive and negative data and news articles are used as an example of neutral speech.
 
In addition to the sentiment analysis we also analyse what compound words are created of our search terms and what adjectives are used to describe them (if they are nouns).


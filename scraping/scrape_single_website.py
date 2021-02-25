#!/usr/bin/env python3

"""
Script for scraping news articles from websites.


Example usage for scraping Spiegel Online articles an storing them in the
file spiegel.json:

    $ python3 scrape.py https://spiegel.de -o spiegel.json


Scraped articles are stored in a JSON file with the following structure:

{
    "<ARTICLE_URL>": {
        "text": "<ARTICLE-TEXT>",
        "title": "<ARTICLE_TITLE>",
        ...
    },
    ...
}

At the top level, each article is uniquely identified with its URL
(<ARTICLE_URL>) and under each URL key you can find the contents ("text"),
title and additional site-dependent metadata.

For example, to print the titles of all articles stored in such a JSON file
("spiegel.json"), you can write:

>>> import json
>>> 
>>> with open('spiegel.json', 'r') as f:
>>>     articles = json.load(f)
>>> for url in articles.keys():
>>>     print(articles[url]['title'])

"""

import argparse
import json
import traceback

import newspaper
from tqdm import tqdm

parser = argparse.ArgumentParser(epilog=__doc__, formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument('url', help='Base URL of a news website')
parser.add_argument(
    '-o',
    help='Path to JSON file in which articles should be stored.',
    default=None
)
parser.add_argument('--language', default='de', help='Language of the articles')
args = parser.parse_args()

url = args.url
outpath = args.o
language = args.language

# Parse site
print('Finding articles...')

# Prepend protocol if necessary
if not url.startswith('https://'):
    url = f'https://{url}'

# Don't memoize articles because we always want to download every
# available article on the site
site = newspaper.build(url, memoize_articles=False)
print(f'Found {len(site.articles)} articles on {url} ({site.brand})')

if len(site.articles) == 0:
    raise RuntimeError(f'No articles found. Aborting...')

scraped_articles = {}
failed_urls = []
empty_urls = []
# Download and parse articles, store in dict (title: content)
for article in tqdm(site.articles):
    try:
        article.download()
        article.parse()
        # Store metadata and article text in the dict
        scraped_articles[article.url] = dict(article.meta_data)
        scraped_articles[article.url]['text'] = article.text
        scraped_articles[article.url]['title'] = article.title
    except newspaper.ArticleException:
        failed_urls.append(article.url)
        traceback.print_exc()

# Print statistics
if len(failed_urls) > 0:
    print(f'URLs of failed articles ({len(failed_urls)}):')
    print('\n'.join(failed_urls))
print(f'Successfully retrieved {len(scraped_articles)} articles.')

if outpath is None:
    outpath = site.brand + '.json'

# Store article collection as JSON
print(f'Storing collection in {outpath}')
with open(outpath, 'w') as f:
    json.dump(scraped_articles, f)

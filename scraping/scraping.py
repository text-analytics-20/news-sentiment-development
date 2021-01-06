"""Library for scraping news articles from websites, based on newspaper"""

import csv
import json
import logging
import os

from dataclasses import dataclass
from typing import Dict, Sequence

import newspaper
from tqdm import tqdm


def setup_logging(log_path: str = '/tmp/scraping.log') -> logging.Logger:
    logger = logging.getLogger('scraping')
    logger.setLevel(logging.DEBUG)
    c_handler = logging.StreamHandler()
    f_handler = logging.FileHandler(log_path)
    c_handler.setLevel(logging.INFO)
    f_handler.setLevel(logging.DEBUG)
    c_format = logging.Formatter('%(levelname)s - %(message)s')
    f_format = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    c_handler.setFormatter(c_format)
    f_handler.setFormatter(f_format)
    logger.addHandler(c_handler)
    logger.addHandler(f_handler)
    logger.propagate = False
    return logger

# Instantiate module logger
logger = setup_logging()



def change_log_file_path(new_log_path):
    """Change file path of log file"""
    for h in logger.handlers:
        if isinstance(h, logging.FileHandler):
            h.close()
            h.baseFilename = new_log_path


@dataclass
class ArticleSource:
    url: str
    date: str


def read_sources(path: str) -> Sequence[ArticleSource]:
    """Read a list of source entries from a tab-separated CSV file.
    
    Each line is expected to have the following format:
    <INDEX>\t<ARTICLE_URL>\t<PUBLICATION_DATE>"""
    article_sources = []
    path = os.path.expanduser(path)
    with open(path, 'r') as f:
        reader = csv.reader(f, delimiter='\t')
        for row in reader:
            if len(row) != 3:
                logger.error(
                    f'{path}: Line {row} has invalid format. '
                    f'Expected 3 tab-separated strings in each row.'
                )
            idx, url, date = row
            article_sources.append(ArticleSource(url=url, date=date))
    return article_sources

def load_article(source: ArticleSource) -> Dict[str, str]:
    """Download and parse article, fill metadata, store date from the given article source"""
    article = newspaper.Article(source.url)
    try:
        article.download()
        article.parse()
    except newspaper.ArticleException:
        logger.debug(f'Could not download {article.url}')
        return None
    # Store metadata and article text in the dict
    entry = dict(article.meta_data)
    entry['text'] = article.text
    entry['title'] = article.title
    entry['date'] = source.date
    return entry


def scrape_articles(sources: Sequence[ArticleSource]) -> Sequence[Dict[str, str]]:
    """Scrape articles from given article sources"""
    scraped_articles = {}
    logger.info('Downloading and parsing articles...')
    for article_source in tqdm(sources):
        entry = load_article(article_source)
        if entry is not None:
            scraped_articles[article_source.url] = entry
    return scraped_articles

def write_to_json(articles: Dict[str, str], json_path: str) -> None:
    """Write article collection dict to a JSON file"""
    logger.info(f'Storing collection in {json_path}')
    json_path = os.path.expanduser(json_path)
    with open(json_path, 'w') as f:
        json.dump(articles, f)

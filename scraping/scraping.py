"""Library for scraping news articles from websites, based on newspaper"""

import csv
import functools
import json
import logging
import os
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from dataclasses import dataclass
from typing import Any, Dict, Optional, Sequence

import newspaper
from tqdm import tqdm

NP_DEFAULT_CONFIG = {
    'language': 'de',
    'fetch_images': False,
    'memoize_articles': False,
    'request_timeout': 7,
}


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


def load_article(
        source: ArticleSource,
        np_config: Optional[Dict[str, Any]] = None
) -> Dict[str, str]:
    """Download and parse article, fill metadata,
    store date from the given article source."""
    np_config = NP_DEFAULT_CONFIG if np_config is None else np_config
    np_article = newspaper.Article(source.url, **np_config)
    try:
        np_article.download()
        np_article.parse()
    except newspaper.ArticleException:
        logger.debug(f'Could not find article {np_article.url}')
        return None
    except Exception:
        # download() may also throw other exceptions, such as:
        # UnicodeDecodeError: 'utf-8' codec can't decode byte X in position Y:
        # invalid continuation byte
        # Therefore we also catch unspecified exceptions here in order to not
        # make the program crash
        logger.debug(f'Error loading {np_article.url}:', exc_info=True)
        return None
    # Initialize article dict with misc. metadata from newspaper (site-dependent!)
    article = dict(np_article.meta_data)
    # Manually ensure text, title, date and url are properly registered
    article['text'] = np_article.text
    article['title'] = np_article.title
    article['date'] = source.date
    article['url'] = source.url
    return article


def filename_from_url(url: str, ext: str = '.json') -> str:
    # Only keep alphanumeric characters because they are definitely safe
    sanitized_url = ''.join(c for c in url if c.isalnum())
    filename = f'{sanitized_url}{ext}'
    return filename


def load_and_store_article(
        source: ArticleSource,
        parent_dir: str,
        np_config: Optional[Dict[str, Any]] = None
) -> None:
    filename = filename_from_url(source.url)
    full_path = f'{parent_dir}/{filename}'
    if os.path.exists(full_path):
        logger.debug(f'{full_path} already exists, skipping...')
        return

    article = load_article(source=source, np_config=np_config)
    if article is not None:
        write_to_json(article, full_path)


def scrape_articles(sources: Sequence[ArticleSource]) -> Sequence[Dict[str, str]]:
    """Scrape articles from given article sources"""
    scraped_articles = {}
    logger.info('Downloading and parsing articles...')
    for article_source in tqdm(sources):
        article = load_article(article_source)
        if article is not None:
            scraped_articles[article_source.url] = article
    return scraped_articles


def scrape_and_store_articles(
        sources: Sequence[ArticleSource],
        parent_dir: str,
        multiprocessing: bool = True,
        num_workers: int = 32
) -> None:
    """Scrape articles from given article sources and immediately store them on disk.
    
    Uses multiprocessing/multithreading."""
    parent_dir = os.path.expanduser(parent_dir)
    # Partially applied function to always store to the same parent dir
    _load_and_store_article = functools.partial(
        load_and_store_article,
        parent_dir=parent_dir
    )
    os.makedirs(parent_dir, exist_ok=True)
    logger.info(f'Downloading and parsing articles, storing in {parent_dir} ...')
    # TODO: Make logging multi-processing-safe
    Executor = ProcessPoolExecutor if multiprocessing else ThreadPoolExecutor
    with Executor(max_workers=num_workers) as executor:
        # Wrapping in list(tqdm(...)) necessary to enable progress bar
        list(tqdm(
            executor.map(_load_and_store_article, sources),
            total=len(sources)
        ))


def write_to_json(articles: Dict[str, str], json_path: str) -> None:
    """Write article collection dict to a JSON file"""
    # logger.debug(f'Storing collection in {json_path}')
    json_path = os.path.expanduser(json_path)
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(articles, f, ensure_ascii=False)

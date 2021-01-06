#!/usr/bin/env python3

"""
Script for scraping news articles from websites.


Example usage for downloading all articles listed in a csv and storing them in the
file articles.json:

    $ python3 collect_articles.py urls.txt -o articles.json


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


"""

import argparse
import logging

from scraping import read_sources, scrape_articles, write_to_json, change_log_file_path

logger = logging.getLogger('scraping')


def main():
    
    parser = argparse.ArgumentParser(epilog=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument(
        'source_path',
        help='Path to a file containing a list of source URLs.'
    )
    parser.add_argument(
        'output_path',
        help='Path to JSON file in which articles should be stored.',
    )
    parser.add_argument(
        '--log-path',
        help='Path to log file (default: /tmp/scraping.log)',
        default='/tmp/scraping.log'
    )
    args = parser.parse_args()

    source_path = args.source_path
    output_path = args.output_path
    log_path = args.log_path

    # Set up logging: Override log file path
    change_log_file_path(log_path)

    # Parse site
    logger.info('Finding articles in file...')
    article_sources = read_sources(source_path)
    if len(article_sources) == 0:
        raise RuntimeError(f'No articles found. Aborting...')
    scraped_articles = scrape_articles(article_sources)
    # Store article collection as JSON
    write_to_json(scraped_articles, output_path)

if __name__ == '__main__':
    main()


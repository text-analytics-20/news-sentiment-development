#!/usr/bin/env python3

"""
Script for scraping news articles from websites.


Example usage for downloading all articles listed in a csv and storing them in the
directory /tmp/news-articles:

    $ python3 collect_articles.py urls.txt /tmp/news-articles


Scraped articles are stored in JSON files with the following structure:

{
    "text": "<ARTICLE-TEXT>",
    "title": "<ARTICLE_TITLE>",
    "date": "<ARTICLE_DATE>",
    "url": "<ARTICLE_URL">
    ...
}

Each article is saved to its own file in the specified directory.
File names are automatically chosen based on the respective article URLs.
In each JSON file you can find the contents ("text"), title, publication date,
URL and additional site-dependent metadata.
"""

import argparse
import logging

from scraping import read_sources, scrape_and_store_articles, change_log_file_path

logger = logging.getLogger('scraping')


def main():
    
    parser = argparse.ArgumentParser(epilog=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument(
        'source_path',
        help='Path to a file containing a list of source URLs.'
    )
    parser.add_argument(
        'output_path',
        help='Path to the directory in which the articles should be stored.',
    )
    parser.add_argument(
        '--log-path',
        help='Path to log file (default: /tmp/scraping.log)',
        default='/tmp/scraping.log'
    )
    parser.add_argument(
        '-m', '--enable-mp',
        help='Enable multiprocessing (faster, but logging may be broken)',
        action='store_true'
    )
    parser.add_argument(
        '-n', '--num-workers',
        help='Number of concurrent worker processes/threads',
        type=int
    )
    args = parser.parse_args()

    source_path = args.source_path
    output_path = args.output_path
    log_path = args.log_path
    enable_mp = args.enable_mp
    num_workers = args.num_workers

    # Set up logging: Override log file path
    change_log_file_path(log_path)

    # Parse site
    logger.info('Finding articles in file...')
    article_sources = read_sources(source_path)
    if len(article_sources) == 0:
        raise RuntimeError(f'No articles found. Aborting...')
    scrape_and_store_articles(
        article_sources,
        parent_dir=output_path,
        multiprocessing=enable_mp,
        num_workers=num_workers
    )

if __name__ == '__main__':
    main()


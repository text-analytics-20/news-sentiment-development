"""Tool for sentiment dataset annotation."""

import argparse
import configparser
import csv
import json
import os
from typing import Sequence, Set

import spacy
from tqdm import tqdm

# Requires `python -m spacy download de_core_news_sm`
nlp = spacy.load('de_core_news_sm')

LABELING_PROMPT = ('\n == Please label sentiment (p = positive, n = negative, '
                   'h = hostile, enter: neutral): ')


# Get search keywords from config.ini found in the same directory
config_path = os.path.join(os.path.dirname(__file__), 'config.ini')
config = configparser.ConfigParser()
config.read(config_path)
SEARCH_KEYWORDS = config.get("ArticleSelection", "search_words").lower().split(", ")


def has_keyword(text: str) -> bool:
    return any(keyword in text.lower() for keyword in SEARCH_KEYWORDS)


def sentencize(texts: Sequence[str]) -> Sequence[str]:
    """Takes a sequence of texts and returns a list of every sentence in every text.
    """
    all_sentences = []
    for doc in tqdm(nlp.pipe(texts, batch_size=40), total=len(texts), desc='Parsing sentences'):
        sents = [s.text.strip() for s in doc.sents]
        all_sentences.extend(sents)
    return all_sentences


def extract_relevant_sections(
        texts: Sequence[str],
        include_next_sentence: bool,
        already_annotated: Set[str]
) -> Sequence[str]:
    """Extract relevant sections from articles.
    Returns a list of sections where keywords are found.
    
    If ``include_next_sentence=False``, these are just the sentences
    containing keywords.
    If ``include_next_sentence=True``, each section additionally contains
    the sentence after the keyword match, or multiple sentences, if they
    also match the keyword."""
    # Set of sentences that are skipped. Contains both already annotated sentences
    # and additionally the sentences that are found during this section extraction
    # process.
    skip = already_annotated.copy()
    sentences = sentencize(texts)
    relevant_sections = []
    for i in range(len(sentences)):
        sentence = sentences[i]
        if sentence in skip:
            continue
        if has_keyword(sentence):
            section = sentence
            skip.add(sentence)
            if include_next_sentence:
                for j in range(i + 1, len(sentences)):
                    # Append each next sentence as a new line...
                    next_sentence = sentences[j]
                    section = f'{sentence}\n{next_sentence}'
                    skip.add(next_sentence)
                    if not has_keyword(next_sentence):
                        # ... and repeat until the next sentence does not contain a keyword
                        break
            relevant_sections.append(section)

    return relevant_sections


def sentiment_annotation(texts: Sequence[str], output_path: str) -> None:
    """Function to facilitate manual sentiment annotation of texts.
    input: texts as iterable: list of articles/ phrases/ words/ ...
    output_path: path to csv file where to write annotated text entries"""

    # translates input to numerical values
    translation = {'p': 0, 'n': 1, '': 2, 'h': 3}
    print("\n == Starting annotation")

    for section in tqdm(texts, desc='Annotating'):
        print(f'\n\n{section}')
        sentiment = input(LABELING_PROMPT)

        #check for valid input
        while sentiment not in translation.keys():
            print(LABELING_PROMPT)
            print(f'\n\n{section}')
            sentiment = input()
        print('\n =======================================================\n\n')
        entry = (section, translation[sentiment])
        write_entry_to_csv(entry, csv_path=output_path)


def write_entry_to_csv(row: Sequence[str], csv_path: str) -> None:
    with open(csv_path, 'a', encoding='utf-8', newline='') as f:
        writer = csv.writer(f, delimiter='\t')
        writer.writerow(row)
        f.flush()
        os.fsync(f)  # Ensure everything has been written


def extract_texts(input_path: str) -> Sequence[str]:
    with open(os.path.expanduser(input_path), 'r') as f:
        articles = json.load(f)
    texts = [article['text'] for article in articles.values()]
    return texts


def get_already_annotated(csv_path: str) -> Set[str]:
    """Gather the set of text sections that have already been annotated in a CSV."""
    if not os.path.exists(csv_path):
        return set()  # Return empty set if file does not already exist
    already_annoated = set()
    with open(csv_path, 'r', encoding='utf-8', newline='') as f:
        reader = csv.reader(f, delimiter='\t')
        for row in reader:
            already_annoated.add(row[0])
    return already_annoated


if __name__ == "__main__":

    parser = argparse.ArgumentParser(epilog=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument(
        'source_path',
        help='Path to JSON file containing relevant articles.'
    )
    parser.add_argument(
        'output_path',
        help='Path to CSV file in which to write the annotated entries.',
    )
    args = parser.parse_args()

    source_path = os.path.expanduser(args.source_path)
    output_path = os.path.expanduser(args.output_path)

    # Extract article text bodies from an article collection (relevant_article.json)
    texts = extract_texts(source_path)
    # Find what has already been annotated (so these parts can be skipped)
    already_annoated = get_already_annotated(output_path)
    if already_annoated:
        print(f'Skipping {len(already_annoated)} sections that have already been annotated in {output_path}')
    # Extract sections (sentences + neighborhoods) from articles where relevant keywords are found
    relevant_sections = extract_relevant_sections(
        texts, include_next_sentence=True, already_annotated=already_annoated
    )
    # Prompt user annotation input and write annotated texts with labels to output CSV file
    sentiment_annotation(relevant_sections, output_path)

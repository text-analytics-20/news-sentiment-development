"""Tool for sentiment dataset annotation."""

import argparse
import csv
import json
import os
from typing import Sequence

import spacy
from tqdm import tqdm

# Requires `python -m spacy download de_core_news_sm`
nlp = spacy.load('de_core_news_sm')


def has_keyword(text: str, keywords=['migra', 'flücht', 'asyl']) -> bool:
    return any(keyword in text for keyword in keywords)


def extract_relevant_sections(texts: Sequence[str], include_next_sentence=True) -> Sequence[str]:
    concat_text = '\n'.join(texts)
    relevant_sections = []
    sentences = [sent.text for sent in nlp(concat_text).sents]  # TODO: Optimize this.
    for i in tqdm(range(len(sentences))):
        sentence = sentences[i]
        if has_keyword(sentence):
            if include_next_sentence and i < len(sentences) - 1:
                next_sentence = sentences[i + 1]
                section = f'{sentence}\n{next_sentence}'
            else:
                section = sentence
            relevant_sections.append(section)

    return relevant_sections


def sentiment_annotation(texts: Sequence[str], output_path: str) -> None:
    """Function to facilitate manual sentiment annotation of texts.
    input: texts as iterable: list of articles/ phrases/ words/ ...
    output_path: path to csv file where to write annotated text entries"""

    # translates input to numerical values
    translation = {'p': 0, 'n': 1, '': 2}
    print(" == Sentiment input: p = positive, n = negative, press enter if neutral:\n")

    for section in texts:
        print(section)
        sentiment = input()

        #check for valid input
        while sentiment not in ["n", "p", ""]:
            print(" == No valid input. p = positive, n = negative, press enter if neutral:\n")
            print(section)
            sentiment = input()
        print('\n    ===================================\n\n')
        entry = (section, translation[sentiment])
        write_entry_to_csv(entry, csv_path=output_path)


def write_entry_to_csv(row: Sequence[str], csv_path: str) -> None:
    with open(csv_path, 'a') as f:
        writer = csv.writer(f, delimiter='\t')
        writer.writerow(row)


def extract_texts(input_path: str) -> Sequence[str]:
    with open(os.path.expanduser(input_path), 'r') as f:
        articles = json.load(f)
    texts = [article['text'] for article in articles.values()]
    return texts


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

    source_path = args.source_path
    output_path = args.output_path

    texts = extract_texts(source_path)
    relevant_sections = extract_relevant_sections(texts, include_next_sentence=True)
    sentiment_annotation(relevant_sections, output_path)

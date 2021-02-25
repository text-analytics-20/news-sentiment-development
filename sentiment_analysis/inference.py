import csv
import json
import traceback
from typing import Sequence

import numpy as np
import pandas as pd
from tqdm import tqdm

from sentiment_analysis import sentimentDictionary as sd
from sentiment_analysis.bert import GSBertPolarityModel


def calulate_sentiment(
        input_path: str,
        output_path: str,
        search_words: list,
        methods: Sequence[str],
        finetuned_sentibert_path: str
):
    # Initialize BERT models
    generic_sentibert, finetuned_sentibert = None, None
    if 'generic_sentibert' in methods:
        generic_sentibert = GSBertPolarityModel("oliverguhr/german-sentiment-bert")
    if 'finetuned_sentibert' in methods:
        finetuned_sentibert = GSBertPolarityModel(finetuned_sentibert_path)

    # get the data from the given file path
    content = pd.read_json(input_path, orient="index")
    content = content[["date", "text", "url", "title"]]

    content = content.sample(20)  # For a quick test run: use only a few samples.

    # create dictionary with output data
    data = {}

    list_len = len(content["text"])
    print("Start calculating sentiment")
    print(f"Total number of articles is: {list_len}")
    for p, row in tqdm(content.iterrows(), total=list_len, dynamic_ncols=True):

        # use only articles that have all needed information
        try:
            text = row['text']
            publisher = row["url"].split("//")[1].split("/")[0].split(".")[1]
            date = row['date']
            title = row['title']
            url = row['url']
        except KeyError:
            traceback.print_exc()
            continue

        # initialize the output data
        data[url] = {
            'publisher': publisher,
            'date': date,
            'title': title,
            'text': text
        }
        # add a key : value pair for all sentiment methods specified in the config

        # 1. use the sentiment dictionary "sentiws"
        if 'sentiws' in methods:
            sentiment_sentiws = sd.analyse_sentiment(text, search_words)
            if sentiment_sentiws == '':
                sentiment_sentiws = float('nan')
            else:
                sentiment_sentiws = float(sentiment_sentiws)
            data[url]['sentiment_sentiws'] = sentiment_sentiws

        # 2. use the generic bert model
        if 'generic_sentibert' in methods:
            sentiment_generic_sentibert = generic_sentibert.analyse_sentiment(text)
            data[url]['sentiment_generic_sentibert'] = sentiment_generic_sentibert

        # 3. use the self trained bert model
        if 'finetuned_sentibert' in methods:
            sentiment_finetuned_sentibert = finetuned_sentibert.analyse_sentiment(text)
            data[url]['sentiment_finetuned_sentibert'] = sentiment_finetuned_sentibert

    # write data to file
    with open(output_path, "w", encoding='utf-8') as f:
        print(f"Write data to {output_path}")
        json.dump(data, f, default=str, ensure_ascii=False)


def absolute_error(
        pred_polarity: float,
        target_label: float,
        label_smoothing: float = 1.0
) -> float:
    target_polarity = {
        0: 1.0 * label_smoothing,  # positive
        1: -1.0 * label_smoothing,  # negative
        2: 0.0  # neutral
    }[target_label]
    abserr = abs(pred_polarity - target_polarity)
    return abserr


def categorical_error(pred_polarity: float, target_label: float) -> float:
    if target_label == 0:  # positive
        return pred_polarity < + (1 / 3)
    if target_label == 1:  # negative
        return pred_polarity > - (1 / 3)
    if target_label == 2:  # neutral
        return abs(pred_polarity) < (1 / 3)


def eval_sentiment(
        senti_eval_input: str,
        senti_eval_output: str,
        search_words: Sequence[str],
        methods: Sequence[str],
        finetuned_sentibert_path: str
):
    print(f'Evaluating sentiment analysis methods on {senti_eval_input}')
    # Initialize BERT models
    generic_sentibert, finetuned_sentibert = None, None
    if 'generic_sentibert' in methods:
        generic_sentibert = GSBertPolarityModel("oliverguhr/german-sentiment-bert")
    if 'finetuned_sentibert' in methods:
        finetuned_sentibert = GSBertPolarityModel(finetuned_sentibert_path)

    label_remap = {3: 1}  # Analogous to training setup: remap "hostile" to "negative"
    texts = []
    labels = []
    with open(senti_eval_input, 'r', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter='\t')
        for row in reader:
            if len(row) != 2:
                raise ValueError('Invalid row encountered.')
            text = row[0]
            label = int(row[1])
            # If the label has an entry in the label_remap dict,
            # it is remapped accordingly. Else, the label is kept.
            label = label_remap.get(label, label)
            texts.append(text)
            labels.append(label)

    # create dictionary with output data
    full_results = {}
    aggregated_results = {}

    # Values lower than 1 make conversion from categorical labels to polarities more smooth
    label_smoothing = 1.0

    for method in methods:
        full_results[method] = {'categorical_errors': [], 'absolute_errors': []}
        aggregated_results[method] = {}

        # Calculate metrics on each entry in the validation dataset
        for text, target_label in tqdm(
                zip(texts, labels),
                total=len(texts),
                dynamic_ncols=True,
                desc=method
        ):

            if method == 'sentiws':
                pred_polarity = sd.analyse_sentiment(text, search_words)
                if pred_polarity == '':
                    pred_polarity = 0.0  # 'nan'
                pred_polarity = float(pred_polarity)
            elif method == 'generic_sentibert':
                pred_polarity = generic_sentibert.analyse_sentiment(text)
            elif method == 'finetuned_sentibert':
                pred_polarity = finetuned_sentibert.analyse_sentiment(text)

            # Calculate error metrics: absolute error (using polarities)
            abserr = absolute_error(
                pred_polarity,
                target_label,
                label_smoothing=label_smoothing
            )
            full_results[method]['absolute_errors'].append(abserr)

            # Alternative error metric: categorical error
            # (bool that indicates if prediction is within the expected interval)
            caterr = categorical_error(pred_polarity, target_label)
            full_results[method]['categorical_errors'].append(caterr)

        # Aggregate metrics
        for metric_name in ['absolute_errors', 'categorical_errors']:
            aggregated_results[method][f'mean_{metric_name[:-1]}'] = np.mean(full_results[method][metric_name])
            aggregated_results[method][f'std_{metric_name[:-1]}'] = np.std(full_results[method][metric_name])

    agr_pd = pd.DataFrame.from_dict(aggregated_results)
    print(f'Aggregated results:\n{agr_pd}\n')

    # write data to file
    with open(senti_eval_output, "w", encoding='utf-8') as f:
        print(f"Write data to {senti_eval_output}")
        json.dump(aggregated_results, f, default=str, ensure_ascii=False)
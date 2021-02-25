"""German news entiment classification using a pretrained BERT model.

SentimentModel class based on https://huggingface.co/oliverguhr/german-sentiment-bert,
    (C) 2020 Oliver Guhr (MIT License)"""

import re
from typing import List

import torch
import torch.nn.functional as F
from transformers import AutoModelForSequenceClassification, AutoTokenizer


# 0: pos, 1: neg, 2: neutral


class GSBertPolarityModel:
    """Code based on
    https://github.com/oliverguhr/german-sentiment-lib/blob/4e5158/germansentiment/sentimentmodel.py
    
    Prediction output form changed from argmax output to polarity score to make it
    more comparable to SentiWS."""

    def __init__(self, model_name: str = "oliverguhr/german-sentiment-bert"):
        self.model = AutoModelForSequenceClassification.from_pretrained(model_name)
        # Always use original tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained("oliverguhr/german-sentiment-bert")

        self.clean_chars = re.compile(r'[^A-Za-züöäÖÜÄß ]', re.MULTILINE)
        self.clean_http_urls = re.compile(r'https*\S+', re.MULTILINE)
        self.clean_at_mentions = re.compile(r'@\S+', re.MULTILINE)

    def replace_numbers(self, text: str) -> str:
        return text.replace("0", " null").replace("1", " eins").replace("2", " zwei") \
            .replace("3", " drei").replace("4", " vier").replace("5", " fünf") \
            .replace("6", " sechs").replace("7", " sieben").replace("8", " acht") \
            .replace("9", " neun")

    def clean_text(self, text: str) -> str:
        text = text.replace("\n", " ")
        text = self.clean_http_urls.sub('', text)
        text = self.clean_at_mentions.sub('', text)
        text = self.replace_numbers(text)
        text = self.clean_chars.sub('', text)  # use only text chars
        text = ' '.join(text.split())  # substitute multiple whitespace with single whitespace
        text = text.strip().lower()
        return text

    @staticmethod
    def probs2polarities(pnn: torch.Tensor) -> torch.Tensor:
        """Transform softmax probs of a [positive, negative, neutral] classifier
        into scalar polarity scores of range [-1, 1].
        High values express positive sentiment, low negative ones negative sentiment.
        Values close to 0 express neutral sentiment."""
        pos = pnn[:, 0]
        neg = pnn[:, 1]
        # Transform range [0, 1] to [-1, 1]
        # Ignore neutrality score as it's implicitly encoded as (1 - pos - neg)
        polarities = pos - neg
        return polarities

    def predict_sentiment_batch(self, texts: List[str]) -> torch.Tensor:
        texts = [self.clean_text(text) for text in texts]
        # Add special tokens takes care of adding [CLS], [SEP], <s>... tokens in the right way for each model.
        input_ids = self.tokenizer.batch_encode_plus(
            texts,
            padding=True,
            add_special_tokens=True,
            truncation=True  # Ensure that the text does not exceed the token limit
        )
        input_ids = torch.tensor(input_ids["input_ids"])

        with torch.no_grad():
            logits = self.model(input_ids)
            probs = F.softmax(logits[0], dim=1)

        polarities = self.probs2polarities(probs)
        return polarities

    def analyse_sentiment(self, text: str) -> float:
        polarity = self.predict_sentiment_batch([text]).item()
        return polarity


def test():
    model = GSBertPolarityModel()
    s = model.predict_sentiment_batch(['Du hirnloser Vollidiot!', 'Ich mag dich sehr.'])
    print("\nSentiment analysis using bert:")
    print("'Du hirnloser Vollidiot!'", "'Ich mag dich sehr.'")
    print(s)
    p = model.analyse_sentiment('Dieser Satz ist relativ neutral. Dieser hier auch.')
    print("For a more neutral sentence:")
    print("'Dieser Satz ist relativ neutral. Dieser hier auch.'")
    print(p)


if __name__ == '__main__':
    test()

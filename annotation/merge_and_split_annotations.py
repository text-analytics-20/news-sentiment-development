"""Script to merge annotations done by multiple team members,
shuffle and split them into train and validation data."""

import csv
import os
import random
from typing import List, Tuple

random.seed(0)

# Where individual annotation CSV files can be found
team_annotations_path = 'data/team_annotations/'
# Where to write resulting dataset split
train_output_path = 'data/train.csv'
validation_output_path = 'data/validation.csv'
validation_proportion = 0.1

team_annotations: List[Tuple[str, str]] = []
# Collect all annotations in one list of (text, label) tuples
for fpath in os.scandir(team_annotations_path):
    with open(fpath.path, 'r', encoding='utf-8', newline='') as f:
        for delim in [',', '\t']:  # Handle different delimiters
            reader = csv.reader(f, delimiter=delim)
            for row in reader:
                if len(row) != 2:
                    break
                text, label = row
                team_annotations.append((text, label))
total_size = len(team_annotations)
print(f'{total_size} samples found in all annotations.')

# Shuffle and randomly split into training and validation sets
random.shuffle(team_annotations)
validation_size = int(total_size * validation_proportion)
validation_data = team_annotations[:validation_size]
train_data = team_annotations[validation_size:]

# Write split
print(f'Writing {len(train_data)} samples to {train_output_path}')
with open(train_output_path, 'w', encoding='utf-8', newline='') as f:
    writer = csv.writer(f, delimiter='\t')
    writer.writerows(train_data)
print(f'Writing {len(validation_data)} samples to {validation_output_path}')
with open(validation_output_path, 'w', encoding='utf-8', newline='') as f:
    writer = csv.writer(f, delimiter='\t')
    writer.writerows(validation_data)

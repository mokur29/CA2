#!/usr/bin/env python

import sys
import re
from sklearn.preprocessing import LabelEncoder

def preprocess_text(text):
    # Perform preprocessing steps such as lowercasing, removing special characters, etc.
    text = text.lower()
    text = re.sub(r"[^a-zA-Z0-9\s]", "", text)
    return text

def mapper():
    # Create a label encoder for encoding classes
    label_encoder = LabelEncoder()

    # Read input from standard input
    for line in sys.stdin:
        # Remove leading/trailing whitespaces and split the line by tabs
        line = line.strip()
        columns = line.split("\t")

        # Skip header line
        if columns[0] == "text":
            continue

        # Get the text and class columns
        text = columns[0]
        class_label = columns[1]
        date = columns[2]
        # Preprocess the text
        preprocessed_text = preprocess_text(text)

        # Encode the class label
        encoded_label = label_encoder.fit_transform([class_label])[0]

        # Emit the preprocessed text and encoded class label
        print(f"{preprocessed_text}\t{encoded_label}\t{date}")

if __name__ == "__main__":
    mapper()

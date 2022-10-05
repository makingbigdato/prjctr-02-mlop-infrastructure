from sklearn.ensemble import RandomForestClassifier
import argparse
import json
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import pickle
import numpy as np


def inference(
    model_path: str,
    data_path: str,
    results_path: str):

    ### Intial Preparation
    # Load data
    # Open and reads file "data"
    with open(data_path) as f:
        dataset = json.load(f) 

    X_test = dataset['x_test']
    y_test = dataset['y_test']

    with open(model_path, "rb") as f:
        clf = pickle.load(f)

    y_pred = clf.predict(X_test)
    y_probas = clf.predict_proba(X_test)

    predictions = {
        "classes": y_pred.tolist(),
        "probas": y_probas.tolist(),
    }

    # save predictions
    with open(results_path, 'w') as f:
        json.dump(predictions, f, indent=2)


if __name__ == "__main__":
    # Defining and parsing the command-line arguments
    # python inference-pipeline.py --model-path=../train-model/cls.pekl --data-path=../load-data/dataset.json --results-path=res.json
    parser = argparse.ArgumentParser(description='Inference on k8s pipeline')

    parser.add_argument('--model-path', type=str, required=True)
    parser.add_argument('--data-path', type=str, required=True)
    parser.add_argument('--results-path', type=str, required=True)

    args = parser.parse_args()

    inference(
        model_path = args.model_path,
        data_path = args.data_path,
        results_path = args.results_path,
    )

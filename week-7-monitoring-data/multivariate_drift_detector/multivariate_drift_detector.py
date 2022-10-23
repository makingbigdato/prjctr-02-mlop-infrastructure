import argparse
import json
import pickle
from alibi_detect.cd import MMDDrift
import numpy as np


def inference(
    model_path: str,
    data_path: str,
    inference_data_path: str,
    threshold: float):

    ### Intial Preparation
    # Load data
    # Open and reads file "data"
    with open(data_path) as f:
        dataset = json.load(f)
    X_train = np.array(dataset['x_train'])
    # y_train = dataset['y_train']

    with open(inference_data_path) as f:
        inference_data = json.load(f)
    X = np.array(inference_data["x_train"])

    with open(model_path, "rb") as f:
        clf = pickle.load(f)

    # Initialize Maximum Mean Discrepancy drift detector
    cd_mmd = MMDDrift(X_train, p_val = threshold, backend='pytorch')
    drift = cd_mmd.predict(X)

    # Simulate handling detected drift and passing alerts forward
    if drift["data"]["is_drift"] == 1:
        print("Alert: data drift detected!")
        raise ValueError(drift)
    print(drift)


if __name__ == "__main__":
    # Defining and parsing the command-line arguments
    # python multivariate-drift-detector.py --model-path=../train-model/cls.pekl --data-path=../load-data/dataset.json --threshold=0.05
    parser = argparse.ArgumentParser(description='Multivariate drift detection')

    parser.add_argument('--model-path', type=str, required=True)
    parser.add_argument('--data-path', type=str, required=True)
    parser.add_argument('--inference-data-path', type=str, required=True)
    parser.add_argument('--threshold', type=float, required=True)

    args = parser.parse_args()

    inference(
        model_path = args.model_path,
        data_path = args.data_path,
        inference_data_path = args.inference_data_path,
        threshold = args.threshold
    )

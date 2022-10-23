import argparse
import json
import pickle
from alibi_detect.cd import KSDrift
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

    # Initialize Kolmogorov-Smirnov drift detector
    train_feature_0 = X_train[:, 0]
    train_feature_1 = X_train[:, 1]

    cd_0 = KSDrift(train_feature_0, p_val=threshold)
    cd_1 = KSDrift(train_feature_1, p_val=threshold)


    drift_0 = cd_0.predict(X[:, 0])
    drift_1 = cd_1.predict(X[:, 1])

    # Simulate handling detected drift and passing alerts forward
    if drift_0["data"]["is_drift"] == 1:
        print("Alert: data drift detected for feature_0!")
        raise ValueError(drift_0, drift_1)
    if drift_1["data"]["is_drift"] == 1:
        print("Alert: data drift detected for feature_1!")
        raise ValueError(drift_0, drift_1)
    
    print("Feature 0:", drift_0)
    print("\n")
    print("Feature 1:", drift_1)


if __name__ == "__main__":
    # Defining and parsing the command-line arguments
    # python univariate_drift_detector.py --model-path=../train-model/cls.pekl --data-path=../load-data/dataset.json --threshold=0.05
    parser = argparse.ArgumentParser(description='Univariate drift detection')

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

import datetime
import os
import pickle
import uuid
import json

import numpy as np
import pandas as pd
from arize.pandas.logger import Client
from arize.utils.types import ModelTypes, Environments, Schema
from sklearn import datasets
from sklearn import ensemble
from sklearn.model_selection import train_test_split
import wandb
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv('API_KEY')
SPACE_KEY = os.getenv('SPACE_KEY')


def map_proba(y_pred, y_pred_proba):
    """
    Input:
    y_pred (1-dim) and y_pred_proba (n-dim) from sklearn
    Output:
    y_pred_scores (1-dim) np.array for the probability of only the predicted class
    """
    y_pred_scores = [y_pred_proba[i][int(y_pred[i])] for i in range(len(y_pred))]
    return np.array(y_pred_scores)


def load_data_and_model():
    # 1 Load train/test/val data
    with open("./training-dataset.json", "rt") as f:
        dataset = json.load(fp=f)
    X_train = dataset["x_train"]
    y_train = dataset["y_train"]
    X_test = dataset["x_test"]
    y_test = dataset["y_test"]

    with open("./validation-dataset.json", "rt") as f:
        dataset = json.load(fp=f)
    X_val = dataset["x_test"]
    y_val = dataset["y_test"]

    # 2 Load pretrained model
    with open("./cls.pekl", "rb") as f:
        clf = pickle.load(f)

    # 3 Use the model to generate predictions
    y_train_pred = clf.predict(X_train)
    y_train_pred_proba = clf.predict_proba(X_train)
    y_train_scores = map_proba(y_train_pred, y_train_pred_proba)
    
    y_test_pred = clf.predict(X_test)
    y_test_pred_proba = clf.predict_proba(X_test)
    y_test_scores = map_proba(y_test_pred, y_test_pred_proba)

    y_val_pred = clf.predict(X_val)
    y_val_pred_proba = clf.predict_proba(X_val)
    y_val_scores = map_proba(y_val_pred, y_val_pred_proba)


    print("Step 1: Load Data & Build Model Done!")
    return (clf, 
            X_train, y_train, y_train_pred, y_train_scores,
            X_test, y_test, y_test_pred, y_test_scores,
            X_val, y_val, y_val_pred, y_val_scores)


def prepare_dataframe(x, y, y_pred, y_score):
    df = pd.DataFrame()
    df["feature_0"] = np.array(x)[:, 0]
    df["feature_1"] = np.array(x)[:, 1]
    df["prediction_label"] = np.array(y_pred).astype(str)
    df["actual_label"] = np.array(y).astype(str)
    df["prediction_score"] = y_score
    df["prediction_id"] = [str(uuid.uuid4()) for _ in range(len(y))]
    print(df.head())
    return df


def log_train_dataframe(train_df, model_id, model_version, arize_client):
    schema = Schema(
        prediction_id_column_name="prediction_id",
        prediction_label_column_name="prediction_label",
        prediction_score_column_name="prediction_score",
        actual_label_column_name="actual_label",
        feature_column_names=["feature_0", "feature_1"],
    )
    res = arize_client.log(
        dataframe=train_df,
        model_id=model_id,
        model_version=model_version,
        model_type=ModelTypes.SCORE_CATEGORICAL,
        environment=Environments.TRAINING,
        schema=schema,
    )
    if res.status_code != 200:
        print(f"future failed with response code {res.status_code}, {res.text}")
    else:
        print(f"future completed with response code {res.status_code}")


def log_val_dataframe(val_df, model_id, model_version, arize_client):
    schema = Schema(
        prediction_id_column_name="prediction_id",
        prediction_label_column_name="prediction_label",
        prediction_score_column_name="prediction_score",
        actual_label_column_name="actual_label",
        feature_column_names=["feature_0", "feature_1"],
    )
    res = arize_client.log(
        dataframe=val_df,
        model_id=model_id,
        model_version=model_version,
        batch_id="validation_test",  # provide a batch_id to distinguish from other validation data set
        model_type=ModelTypes.SCORE_CATEGORICAL,
        environment=Environments.VALIDATION,
        schema=schema,
    )
    if res.status_code != 200:
        print(f"future failed with response code {res.status_code}, {res.text}")
    else:
        print(f"future completed with response code {res.status_code}")


def log_test_dataframe(test_df, model_id, model_version, arize_client):
    schema = Schema(
        prediction_id_column_name="prediction_id",
        timestamp_column_name="prediction_ts",
        prediction_label_column_name="prediction_label",
        prediction_score_column_name="prediction_score",
        actual_label_column_name="actual_label",
        feature_column_names=["feature_0", "feature_1"],
    )
    res = arize_client.log(
        dataframe=test_df,
        model_id=model_id,
        model_version=model_version,
        model_type=ModelTypes.SCORE_CATEGORICAL,
        environment=Environments.PRODUCTION,
        schema=schema,
    )
    if res.status_code != 200:
        print(f"future failed with response code {res.status_code}, {res.text}")
    else:
        print(f"future completed with response code {res.status_code}")


if __name__ == "__main__":
    (clf, 
        X_train, y_train, y_train_pred, y_train_scores,
        X_test, y_test, y_test_pred, y_test_scores,
        X_val, y_val, y_val_pred, y_val_scores) = load_data_and_model()

    train_df = prepare_dataframe(X_train, y_train, y_train_pred, y_train_scores)
    test_df = prepare_dataframe(X_test, y_test, y_test_pred, y_test_scores)
    val_df = prepare_dataframe(X_val, y_val, y_val_pred, y_val_scores)

    # add timestamp to simulate production environment
    current_time = datetime.datetime.now().timestamp()
    earlier_time = (datetime.datetime.now() - datetime.timedelta(days=30)).timestamp()
    optional_prediction_timestamps = np.linspace(
        earlier_time, current_time, num=len(y_test)
    )
    test_df["prediction_ts"] = pd.Series(optional_prediction_timestamps.astype(int))

    arize_client = Client(space_key=SPACE_KEY, api_key=API_KEY)
    # Saving model metadata for passing in later
    model_id = "random_forest_clf"
    model_version = "latest"
    print("Step 2: Import and Setup Arize Client Done! Now we can start using Arize!")

    log_train_dataframe(train_df, model_id, model_version, arize_client)
    log_val_dataframe(val_df, model_id, model_version, arize_client)
    log_test_dataframe(test_df, model_id, model_version, arize_client)
    print("DONE")

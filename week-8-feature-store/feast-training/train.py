from datetime import datetime
import pandas as pd
import typer
from sklearn.ensemble import RandomForestRegressor
from joblib import dump
from feast import FeatureStore


def get_df(repo_path: str):
    # Note: see https://docs.feast.dev/getting-started/concepts/feature-retrieval for 
    # more details on how to retrieve for all entities in the offline store instead
    entity_df = pd.DataFrame.from_dict(
        {
            # entity's join key -> entity values
            "driver_id": [1001, 1002, 1003],
            # "event_timestamp" (reserved key) -> timestamps
            "event_timestamp": [
                datetime(2021, 4, 12, 10, 59, 42),
                datetime(2021, 4, 12, 8, 12, 10),
                datetime(2021, 4, 12, 16, 40, 26),
            ],
            # (optional) label name -> label values. Feast does not process these
            "label_driver_reported_satisfaction": [1, 5, 3],
            # values we're using for an on-demand transformation
            "val_to_add": [1, 2, 3],
            "val_to_add_2": [10, 20, 30],
        }
    )

    store = FeatureStore(repo_path=repo_path)

    training_df = store.get_historical_features(
        entity_df=entity_df,
        features=[
            "driver_hourly_stats:conv_rate",
            "driver_hourly_stats:acc_rate",
            "driver_hourly_stats:avg_daily_trips",
            "transformed_conv_rate:conv_rate_plus_val1",
            "transformed_conv_rate:conv_rate_plus_val2",
        ],
    ).to_df()

    print("----- Feature schema -----\n")
    print(training_df.info())

    print()
    print("----- Example features -----\n")
    print(training_df.head())
    return training_df


def train(df: pd.DataFrame, model_path: str):
    target = "label_driver_reported_satisfaction"
    print("label_driver_reported_satisfaction")
    print(df.head())

    X = df[df.columns.drop(target).drop("event_timestamp")]
    y = df[[target]].to_numpy().ravel()
    print(X.head())
    print("y", y)

    reg = RandomForestRegressor()
    reg.fit(X, y)
    # Save model
    dump(reg, model_path)


def main(repo_path: str = "/train/features/", model_path: str = "model.bin"):
    train_df = get_df(repo_path)
    train(train_df, model_path)
    

if __name__ == "__main__":
    typer.run(main)
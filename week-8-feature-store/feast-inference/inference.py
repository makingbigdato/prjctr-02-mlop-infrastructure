from datetime import datetime
import argparse
from typing import List, Text
import pandas as pd
from joblib import load
from feast import FeatureStore

from fastapi import FastAPI
from pydantic import BaseModel


class DriverRankingModel:
    def __init__(self, model_path: str, repo_path: str):
        # Load model
        self.model = load(model_path)

        # Set up feature store
        self.fs = FeatureStore(repo_path=repo_path)

    def predict(self, driver_ids: List[int]):
        # Read features from Feast
        driver_features = self.fs.get_online_features(
            entity_rows=[{"driver_id": driver_id} for driver_id in driver_ids],
            features=[
                "driver_hourly_stats:conv_rate",
                "driver_hourly_stats:acc_rate",
                "driver_hourly_stats:avg_daily_trips",
            ],
        )
        df = pd.DataFrame.from_dict(driver_features.to_dict())

        print(df.columns)

        print(df.head())

        # Make prediction
        df["prediction"] = self.model.predict(df[sorted(df)])

        # Choose best driver
        best_driver_id = df["driver_id"].iloc[df["prediction"].argmax()]

        # return best driver
        return best_driver_id


# ----------------------
model = DriverRankingModel(model_path="/train/model/model.bin", repo_path="/train/features/")

app = FastAPI()

class RequestBody(BaseModel):
    driver_ids: List[int]


class ResponseBody(BaseModel):
    best_driver: int


@app.post("/best-driver", response_model=ResponseBody)
def inference_response(request: RequestBody):
    best_driver = model.predict(request.driver_ids)
    return {"best_driver": best_driver}


@app.get("/", status_code=200)
async def status():
    return {"status": "ok"}

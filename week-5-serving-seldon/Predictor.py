from typing import Dict, List, Optional, Union
import numpy as np
from joblib import load
from minio import Minio
import os

ACCESS_KEY = os.environ['ACCESS_KEY']
SECRET_KEY = os.environ['SECRET_KEY']
MINIO_URI = os.environ['MINIO_URI']

class Predictor:
    def __init__(self):
        self.client = Minio(
            endpoint=MINIO_URI,
            access_key=ACCESS_KEY,
            secret_key=SECRET_KEY,
            secure=False,
        )
        self.bucket_name = "models"
        self.file = "model.joblib"
        self.save_path = "/tmp/" + self.file
        self.client.fget_object(self.bucket_name, object_name=self.file, file_path=self.save_path)
        self.clf = load(self.save_path)

    def predict(self, X: Union[np.ndarray, List, str, bytes, Dict], names: Optional[List[str]] = None, meta: Optional[Dict] = None) -> Union[np.ndarray, List, str, bytes, Dict]:
        print(X)
        print(names)
        print(meta)
        prediction = self.clf.predict(X)
        return prediction

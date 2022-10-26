import os
import pickle
from typing import Dict, Iterable, List, Optional, Union
from dataclasses import dataclass
import logging
import time
import numpy as np
import wandb
from filelock import FileLock

logger = logging.getLogger()
logging.basicConfig()

PROJECT = "artifact-storage"
ENTITY = "yevhen-k-team"
MODEL_PATH = "./"
ARTIFACT = "cls.pekl"
MODEL_LOCK = ".lock-file"
run = wandb.init(project=PROJECT, entity=ENTITY)

@dataclass
class Score:
    tp: int = 0
    fp: int = 0
    tn: int = 0
    fn: int = 0


class Predictor:
    def __init__(self, tag: str = "latest"):
        self.scores = Score()
        self.tag = tag
        self.__download_model(MODEL_PATH, self.tag)
        with open(f"{MODEL_PATH}{ARTIFACT}", "rb") as f:
            self.clf = pickle.load(f)
        self.__inference_time = 0
        self.__num_requests = 0
    
    def __download_model(self, model_path: str, tag: str):
        with FileLock(MODEL_LOCK):
            if not os.path.exists(f"{MODEL_PATH}{ARTIFACT}"):
                artifact = run.use_artifact(f'{ENTITY}/{PROJECT}/model:{tag}', type='model')
                artifact_dir = artifact.download(root=model_path)
                logger.info(artifact_dir)
                wandb.run.finish()

    def predict(self, X: Union[np.ndarray, List, str, bytes, Dict], names: Optional[List[str]] = None, meta: Optional[Dict] = None) -> Union[np.ndarray, List, str, bytes, Dict]:
        logger.info(X)
        logger.info(names)
        logger.info(meta)
        start = time.perf_counter()
        prediction = self.clf.predict(X)
        self.__inference_time = time.perf_counter() - start
        self.__num_requests += 1

        return prediction

    def metrics(self):
        return [
            {"type": "GAUGE", "key": "inference_time", "value": self.__inference_time},
            {"type": "TIMER", "key": "inference_time_dist", "value": self.__inference_time},
            {"type": "GAUGE", "key": "true_pos", "value": self.scores.tp},
            {"type": "GAUGE", "key": "true_neg", "value": self.scores.fn},
            {"type": "GAUGE", "key": "false_pos", "value": self.scores.fn},
            {"type": "GAUGE", "key": "false_neg", "value": self.scores.fp},
            {"type": "COUNTER", "key": "request_count", "value": self.__num_requests}
        ]

    def health_status(self):
        response = self.clf.predict([[1, 2], [2, 1]])
        assert len(response) == 2, "health check returning bad predictions"
        return response

    def send_feedback(self, 
                    features: Union[np.ndarray, str, bytes],
                    feature_names: Iterable[str],
                    reward: float,
                    truth: Union[np.ndarray, str, bytes],
                    routing: Union[int, None]
    ):
        """
        Feedback to user model

        Parameters
        ----------
        features
            A payload
        feature_names
            Payload column names
        reward
            Reward
        truth
            True outcome
        routing
            Optional routing

        Returns
        -------
            Optional payload
        """
        predictions = self.clf.predict(features)
        assert len(predictions) == len(features) == len(truth), "failed to make prediction, array sizes mismatch"
        
        for prediction, trth in zip(predictions, truth):
            if int(trth) == 1:
                if int(prediction) == int(trth):
                    self.scores.tp += 1
                else:
                    self.scores.fn += 1
            else:
                if int(prediction) == int(trth):
                    self.scores.tn += 1
                else:
                    self.scores.fp += 1
        return []  # Ignore return statement as its not used

import os
from pathlib import Path
from minio import Minio
from minio.error import S3Error
from sklearn.datasets import make_moons
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from joblib import dump, load
import numpy as np


MODEL = "model.joblib"
MODEL_DIR = "./weights/"
MODEL_SAVE_PATH = f"{MODEL_DIR}{MODEL}"
client = Minio(
        "localhost:8080",
        access_key="miniouser",
        secret_key="miniopassword",
        secure=False,
    )


def train_model():
    X, y = make_moons(n_samples=200, noise=0.3, random_state=0)
    X = StandardScaler().fit_transform(X)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.4, random_state=42
    )
    clf = RandomForestClassifier(max_depth=5, n_estimators=10, max_features=1, random_state=1337)
    clf.fit(X_train, y_train)
    score = clf.score(X_test, y_test)
    y_pred = clf.predict(X_test)
    y_probas = clf.predict_proba(X_test)
    print(f"Classification score: {score}")
    if not os.path.exists(MODEL_DIR):
        os.mkdir(MODEL_DIR)
    dump(clf, MODEL_SAVE_PATH) 
    clf_restored = load(MODEL_SAVE_PATH)
    assert np.isclose(score, clf_restored.score(X_test, y_test), atol=1e-5), "Mode restoration failed"
    print("TRAINING DONE")


def upload_model():
    found = client.bucket_exists("models")
    if not found:
        client.make_bucket("models")
    else:
        print("Bucket 'models' already exists")

    # Upload './file_uploader.py' as object name
    # 'file_uploader.py' to bucket 'models'.
    client.fput_object(
        bucket_name="models", object_name=MODEL, file_path=MODEL_SAVE_PATH,
    )
    print(
        f"{MODEL_SAVE_PATH} is successfully uploaded as "
        f"object {MODEL} to bucket 'models'."
    )


if __name__ == "__main__":
    train_model()
    upload_model()

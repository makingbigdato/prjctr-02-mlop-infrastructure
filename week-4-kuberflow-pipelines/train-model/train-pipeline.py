from sklearn.ensemble import RandomForestClassifier
import argparse
import json
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import pickle
import numpy as np


def train(
    dataset_path: str,
    scores_path: str,
    out_model_path: str,
    max_depth: int = 5, 
    n_estimators: int = 10, 
    max_features: int = 1, 
    random_state: int = 1337):

    ### Intial Preparation
    # Load data
    # Open and reads file "data"
    with open(dataset_path) as f:
        dataset = json.load(f) 

    X_train = dataset['x_train']
    y_train = dataset['y_train']
    X_test = dataset['x_test']
    y_test = dataset['y_test']

    clf = RandomForestClassifier(
        max_depth=max_depth, 
        n_estimators=n_estimators, 
        max_features=max_features, 
        random_state=random_state)
    clf.fit(X_train, y_train)

    y_pred = clf.predict(X_test)
    y_probas = clf.predict_proba(X_test)

    score = clf.score(X_test, y_test)
    ps = precision_score(y_test, y_pred)
    rc = recall_score(y_test, y_pred)
    acc = accuracy_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)

    print("-"*20)
    print(f"Classification score: {score}")
    print(f"Precision score: {ps}")
    print(f"Accuracy score: {acc}")
    print(f"F1 score: {f1}")
    print(f"Recall score: {rc}")

    scores = {
        "accuracy": acc,
        "precision": ps,
        "f1": f1,
        "recall": rc
    }

    # save scores
    with open(scores_path, 'w') as f:
        json.dump(scores, f, indent=2)
    
    # save model
    model_bytes = pickle.dumps(clf)
    with open(out_model_path, "wb") as f:
        f.write(model_bytes)
    
    # test if model saved properly
    print("test saved model")
    with open(out_model_path, "rb") as f:
        model_bytes = f.read()
    clf_restored = pickle.loads(model_bytes)
    assert np.isclose(score, clf_restored.score(X_test, y_test), atol=1e-5), "Mode restoration failed"


if __name__ == "__main__":
    # Defining and parsing the command-line arguments
    # python train-pipeline.py --dataset-path=../load-data/dataset.json --scores-path=scores.json --out-model-path=cls.pekl --max-depth=5 --n-estimators=10 --max-features=1 --random-state=1337
    parser = argparse.ArgumentParser(description='Train on k8s pipeline')

    parser.add_argument('--dataset-path', type=str, required=True)
    parser.add_argument('--scores-path', type=str, required=True)
    parser.add_argument('--out-model-path', type=str, required=True)
    parser.add_argument('--max-depth', type=int, required=True)
    parser.add_argument('--n-estimators', type=int, required=True)
    parser.add_argument('--max-features', type=int, required=True)
    parser.add_argument('--random-state', type=int, required=True)

    args = parser.parse_args()

    train(
        dataset_path = args.dataset_path,
        scores_path = args.scores_path,
        out_model_path = args.out_model_path,
        max_depth = args.max_depth,
        n_estimators = args.n_estimators,
        max_features = args.max_features,
        random_state = args.random_state,
    )

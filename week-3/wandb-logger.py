from typing import Tuple
import wandb
from sklearn.datasets import make_moons
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier


wandb.init(project="test-project", entity="yevhen-k-team")


def main():
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

    wandb.sklearn.plot_classifier(clf, 
        X_train, X_test, y_train, y_test, 
        y_pred, y_probas, ["0", "1"],
        model_name="RandomForest", feature_names=None)


if __name__ == "__main__":
    main()

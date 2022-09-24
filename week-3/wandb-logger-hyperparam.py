import wandb
from sklearn.datasets import make_moons
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier


SWEEP_CONFIG = {
    'program': 'wandb-logger-hyperparam.py',
    'method': 'grid', 
    'metric': {'goal': 'maximize', 'name': 'accuracy'},
    'parameters': {
        'n_estimators': {
            'values': [100, 150, 200]
        },
        'criterion' : {
            'values': ["gini", "entropy"]
        },
    }
}


def train():
    config_defaults = {
        "n_estimators": 100,
        "criterion": "gini"
    }
    wandb.init(config=config_defaults, project="hyperparam-tuning")
    config = wandb.config
    
    X, y = make_moons(n_samples=200, noise=0.3, random_state=0)
    X = StandardScaler().fit_transform(X)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.4, random_state=42
    )
    clf = RandomForestClassifier(max_depth=5, 
        n_estimators=config.n_estimators, 
        criterion=config.criterion,
        max_features=1, 
        random_state=1337)
    clf.fit(X_train, y_train)
    score = clf.score(X_test, y_test)
    y_pred = clf.predict(X_test)
    y_probas = clf.predict_proba(X_test)
    print(f"Classification score: {score}")

    wandb.sklearn.plot_classifier(clf, 
        X_train, X_test, y_train, y_test, 
        y_pred, y_probas, ["0", "1"],
        model_name="RandomForest", feature_names=None)
    wandb.log({"accuracy": score})


def main():
    sweep_id = wandb.sweep(SWEEP_CONFIG, project="hyperparam-tuning")
    wandb.agent(sweep_id, function=train, count=6)
    wandb.finish()


if __name__ == "__main__":
    main()

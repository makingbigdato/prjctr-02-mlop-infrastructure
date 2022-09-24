from aim import Run
from sklearn.datasets import make_moons
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score


def main():
    run = Run(experiment="RandomForest")
    # set training hyperparameters
    run['hparams'] = {
        'n_estimator': [10, 100, 200],
        'criterion': 'gini',
    }
    
    X, y = make_moons(n_samples=200, noise=0.3, random_state=0)
    X = StandardScaler().fit_transform(X)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.4, random_state=42
    )
    # log metric
    for i in range(len(run['hparams']['n_estimator'])):
        clf = RandomForestClassifier(max_depth=5,
                                     n_estimators=run['hparams']['n_estimator'][i],
                                     criterion=run['hparams']['criterion'],
                                     max_features=1,
                                     random_state=1337)
        clf.fit(X_train, y_train)
        score = clf.score(X_test, y_test)
        y_pred = clf.predict(X_test)
        y_probas = clf.predict_proba(X_test)
        ps = precision_score(y_test, y_pred)
        rc = recall_score(y_test, y_pred)
        acc = accuracy_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred)
        print("-"*20)
        print(f"Experiment for {run['hparams']['n_estimator'][i]} estimators")
        print(f"Classification score: {score}")
        print(f"Precision score: {ps}")
        print(f"Accuracy score: {acc}")
        print(f"F1 score: {f1}")
        print(f"Recall score: {rc}")
        run.track(ps, name='precision')
        run.track(acc, name='accuracy')
        run.track(f1, name='f1_score')
        run.track(rc, name='recall')
        

if __name__ == "__main__":
    main()

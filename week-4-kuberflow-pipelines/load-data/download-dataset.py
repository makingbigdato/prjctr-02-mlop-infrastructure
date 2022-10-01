from sklearn.datasets import make_moons
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import argparse
import json


def download_dataset(n_samples=200, noise=0.3, random_state=0, out_file="dataset.json"):
    X, y = make_moons(n_samples=n_samples, noise=noise, random_state=random_state)
    X = StandardScaler().fit_transform(X)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.4, random_state=42
    )
    data = {
        "x_train": X_train.tolist(),
        "y_train": y_train.tolist(),
        "x_test": X_test.tolist(),
        "y_test": y_test.tolist()
    }

    # Saves the json object into a file
    with open(out_file, "w") as f:
        json.dump(data, f, indent=2)


if __name__ == "__main__":
    # python download-dataset.py --n-samples=300 --noise=0.3 --random-state=0 --out-file=dataset.json
    parser = argparse.ArgumentParser()
    parser.add_argument('--n-samples', type=int, required=True)
    parser.add_argument('--noise', type=float, required=True)
    parser.add_argument('--random-state', type=int, required=True)
    parser.add_argument('--out-file', type=str, required=True)

    args = parser.parse_args()

    download_dataset(
        n_samples=args.n_samples,
        noise=args.noise, 
        random_state=args.random_state, 
        out_file=args.out_file,
    )
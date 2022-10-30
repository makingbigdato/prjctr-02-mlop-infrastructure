# Feature store

## PR1. Instructions on how to setup feast feature store (you can choose another feature store)

### Install and Initialize Feast

Follow the [tutorial](https://docs.feast.dev/getting-started/quickstart) to install and configure `feast` feature storage.

1. Install feast

```bash
pip install feast
```

2. Bootstrap feast repo

```bash
feast init week8fs
cd week8fs/feature_repo
```

3. Register feature definitions and deploy your feature store

The `apply` command scans python files in the current directory for feature view/entity definitions, registers the objects, and deploys infrastructure. In particular, all definitions are in `example_repo.py` file.

```bash
feast apply
```

One can create all the files manually. You have to specify:
1. `feature_store.yaml` 

```yaml
project: week8fs
# By default, the registry is a file (but can be turned into a more scalable SQL-backed registry)
registry: data/registry.db
# The provider primarily specifies default offline / online stores & storing the registry in a given cloud
provider: local
online_store:
    type: sqlite
    path: data/online_store.db
entity_key_serialization_version: 2
```

The `feature_store.yaml` file configures the key overall architecture of the feature store.
The provider value sets default offline and online stores.

- The offline store provides the compute layer to process historical data (for generating training data & feature values for serving).
- The online store is a low latency store of the latest feature values (for powering real-time inference).

Valid values for provider in feature_store.yaml are:
- local: use a SQL registry or local file registry. By default, use a file / Dask based offline store + SQLite online store
- gcp: use a SQL registry or GCS file registry. By default, use BigQuery (offline store) + Google Cloud Datastore (online store)
- aws: use a SQL registry or S3 file registry. By default, use Redshift (offline store) + DynamoDB (online store)

2. Definitions and deploy for feature store in python file
3. Then just run `feast apply`


## PR2. Training pipeline which pulls data from the feature store

### Local Training on Historical Data

Run:

```bash
python local-train.py week8fs/feature_repo/ model.bin
```

### Docker training pipeline

Build and run docker:

```bash
cd feast-training
docker build --rm -t feast-training .
```

Run docker:
```bash
docker run -it -v $PWD/features:/train/features -v $PWD/data:/train/data -p 8080:8080 feast-training:latest /bin/bash
```

Apply feast schema:
```bash
cd features/
feast apply
```

Run training:
```bash
cd /train
python train.py
```
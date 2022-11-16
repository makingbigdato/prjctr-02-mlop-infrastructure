# Final Project

Concrete defect detection with the use of computer vision.


## Basic infrastructure options:

> minikube, Airflow, MinIO


## Infrastructure Setup

> minikube, Airflow, MinIO

### Cluster setup

Create cluster:

```bash
minikube start --cpus=4 --memory=10Gi
```


### Create MinIO storage

Based on https://github.com/kubernetes/examples/tree/master/staging/storage/minio

Deploy:

```bash
kubectl create -f k8s/minio-standalone.yaml
```

Access UI and API:

```bash
kubectl port-forward svc/minio-ui 9001:9001 --address 0.0.0.0
kubectl port-forward svc/minio-api 9000:9000 --address 0.0.0.0
```

Update local minio config (`~/.miniocli/config.json`) with:

```json
		"project": {
			"url": "http://localhost:9000",
			"accessKey": "minio",
			"secretKey": "minio123",
			"api": "S3v4",
			"path": "auto"
		},
```

OR use CLI:

```bash
miniocli alias set project http://localhost:9000 minio minio123
```

Check config state:

```bash
miniocli alias ls
```

Test connection to the `project`

```bash
miniocli admin info project
```

Response:
```
●  localhost:9000
   Uptime: 6 minutes 
   Version: 2022-11-08T05:27:07Z
   Network: 1/1 OK 
   Drives: 1/1 OK 
   Pool: 1

Pools:
   1st, Erasure sets: 1, Disks per erasure set: 1

1 drive online, 0 drives offline
```

### Upload Dataset

Upload dataset with the use of minio cli tool.

Create bucket:

```bash
miniocli mb project/dataset
```

Upload dataset:

```bash
miniocli cp --recursive dataset/ project/dataset
```


### Airflow setup


Follow the [instructions](https://airflow.apache.org/docs/apache-airflow/stable/start.html) to install standalone airflow.

```bash
# Airflow needs a home. `~/airflow` is the default, but you can put it
# somewhere else if you prefer (optional)
cd training-pipeline
export AIRFLOW_HOME=$(pwd)/airflow-home

# Install Airflow using the constraints file
AIRFLOW_VERSION=2.4.1
PYTHON_VERSION="$(python --version | cut -d " " -f 2 | cut -d "." -f 1-2)"
# For example: 3.7
CONSTRAINT_URL="https://raw.githubusercontent.com/apache/airflow/constraints-${AIRFLOW_VERSION}/constraints-${PYTHON_VERSION}.txt"
# For example: https://raw.githubusercontent.com/apache/airflow/constraints-2.4.1/constraints-3.7.txt
pip install "apache-airflow==${AIRFLOW_VERSION}" --constraint "${CONSTRAINT_URL}"

# The Standalone command will initialize the database, make a user,
# and start all components for you.
airflow standalone
```


#### Install kubeflow pipelines

1. Install Apache Kubernetes Provider

```bash
pip install apache-airflow-providers-cncf-kubernetes
```

2. Attach volumes to the cluster

For more info follow the [documentation](https://kubernetes.io/docs/tasks/configure-pod-container/configure-persistent-volume-storage/).


```bash
kubectl apply -f k8s/airflow-volumes.yaml
```


## Training Pipeline

### Dataset Downloader Image

```bash
cd training-pipeline/artefact-handler

docker build --rm -t artefact-handler .
docker tag artefact-handler:latest yevhenk10s/artefact-handler:latest
docker push yevhenk10s/artefact-handler:latest
```

Test the image:

```bash
docker run -it yevhenk10s/artefact-handler:latest bash

mc alias set project http://192.168.1.104:9000 minio minio123
mc admin info project
```

Response should be as follows:

```
●  192.168.1.104:9000
   Uptime: 2 hours 
   Version: 2022-11-08T05:27:07Z
   Network: 1/1 OK 
   Drives: 1/1 OK 
   Pool: 1

Pools:
   1st, Erasure sets: 1, Drives per erasure set: 1

234 MiB Used, 1 Bucket, 40,000 Objects
1 drive online, 0 drives offline
```

### Dataset Tester Image

```bash
cd training-pipeline/dataset-tester

docker build --rm -t dataset-tester .
docker tag dataset-tester:latest yevhenk10s/dataset-tester:latest
docker push yevhenk10s/dataset-tester:latest
```

```bash
python -m pytest -s test_dataset.py --dataset-path /tmp/dataset
```

Test the image:

```bash
docker run -it -v $PWD/dataset/:/tmp/dataset yevhenk10s/dataset-tester:latest python -m pytest -s test_dataset.py --dataset-path /tmp/dataset
```


### Training Image

Build an image:

```bash
cd training-pipeline/trainer

docker build --rm -t trainer .
docker tag trainer:latest yevhenk10s/trainer:latest
docker push yevhenk10s/trainer:latest
```

Test training locally:

```bash
python main.py ../../dataset . 1 
```

Check the image:

```bash
mkdir model
docker run -it --ipc=host --gpus all -v $PWD/dataset/:/tmp/dataset -v $PWD/model:/train/model yevhenk10s/trainer:latest python main.py /tmp/dataset ./model 1
ls -lah ./model
```


#### Testing Training Code

Test the code locally:

```bash
cd training-pipeline/trainer
python -m pytest -s test_code.py --dataset-path ../../dataset --save-to . --epochs 1
```

Test the code within docker:

```bash
docker run -it --ipc=host --gpus all -v $PWD/dataset/:/tmp/dataset -v $PWD/model:/train/model yevhenk10s/trainer:latest python -m pytest -s test_code.py --dataset-path /tmp/dataset --save-to . --epochs 1
```

#### Testing Model

Test the model locally:

```bash
cd training-pipeline/trainer
python -m pytest -s test_model.py --dataset-path ../../dataset --save-to . --epochs 1
```

Test the model within docker:

```bash
docker run -it --ipc=host --gpus all -v $PWD/dataset/:/tmp/dataset -v $PWD/model:/train/model yevhenk10s/trainer:latest python -m pytest -s test_model.py --dataset-path /tmp/dataset --save-to . --epochs 1
```


#### All Tests At Once

```bash
python -m pytest -s test_* --dataset-path ../../dataset --save-to . --epochs 1
```

```bash
docker run -it --ipc=host --gpus all -v $PWD/dataset/:/tmp/dataset -v $PWD/model:/train/model yevhenk10s/trainer:latest python -m pytest -s test_code.py test_model.py --dataset-path /tmp/dataset --save-to . --epochs 1
```

### AIM Experiment Tracking

#### Build AIM Image

```bash
cd training-pipeline/aim-k8s

docker build --rm -t aim-k8s -f Dockerfile .
docker tag aim-k8s:latest yevhenk10s/aim-k8s:latest
docker push yevhenk10s/aim-k8s:latest
```

Check image locally;

```bash
mkdir aim
docker run -it -v $PWD/aim:/aim -p 43801:43800 -p 53801:53800 yevhenk10s/aim-k8s:latest 'bash -c "aim init --repo /aim && aim server --repo /aim | aim up --host 0.0.0.0 --port 43800 --workers 2 --repo /aim"'
ls aim/.aim
```

#### Start AIM On Cluster

```bash
kubectl apply -f k8s/aim-standalone.yaml
```

Make port forwarding:

1. UI

```bash
kubectl port-forward deployments/aim-deployment 43800:43800 --address 0.0.0.0
```

2. Backend

```bash
kubectl port-forward deployments/aim-deployment 53800:53800 --address 0.0.0.0
```

Aim UI is now available in http://localhost:43800 and http://192.168.1.104:43800/


## Inference Pipeline

Because the project is developed, tested, and deployed locally with the use of **`minikube`** we won't be able to start seldon.

### Build Inference Image

```bash
cd inference-serving

docker build --rm -t inference .
docker tag inference:latest yevhenk10s/inference:latest
docker push yevhenk10s/inference:latest
```

#### Test Code Locally

```bash
cd inference-serving
ENDPOINT="192.168.1.104:9000" ACCESS_KEY="minio" SECRET_KEY="minio123" uvicorn app:app --reload
```

```bash
curl -X 'POST' \
  'http://127.0.0.1:8000/predict' \
  -H 'accept: application/json' \
  -H 'Content-Type: multipart/form-data' \
  -F 'file=@path-to-file.png;type=image/png'
>>> {"class":"pos"}
```

#### Test Image Locally

```bash
docker run -it -p 8000:8000 --env ENDPOINT="192.168.1.104:9000" --env ACCESS_KEY="minio" --env SECRET_KEY="minio123" yevhenk10s/inference:latest uvicorn app:app --reload --host=0.0.0.0
```

```bash
curl -X 'POST' \
  'http://127.0.0.1:8000/predict' \
  -H 'accept: application/json' \
  -H 'Content-Type: multipart/form-data' \
  -F 'file=@path-to-file.png;type=image/png'
>>> {"class":"pos"}
```

### Deploy Inference Service

```bash
kubectl apply -f k8s/inference-service.yaml
```

```bash
kubectl port-forward svc/inference-service 8000:8000 --address 0.0.0.0
```

#### Test Deployed Service

```bash
curl http://localhost:8000/status

>>> {"status":"ok"}
```

```bash
curl -X 'POST' \
  'http://127.0.0.1:8000/predict' \
  -H 'accept: application/json' \
  -H 'Content-Type: multipart/form-data' \
  -F 'file=@path-to-file.png;type=image/png'
>>> {"class":"pos"}
```

## TODOs
- Data drift for inference pipeline
- try to implemet GPU support in Airflow pipelines
  - `--ipc=host`
  - `num_workers=4`
  - `--gpus=all`
- check sporadic fails of `test_loss_decrease()` test

## References
- Data Drift
  - https://docs.seldon.io/projects/alibi-detect/en/stable/od/methods/vae.html
  - https://docs.seldon.io/projects/alibi-detect/en/stable/examples/od_vae_cifar10.html
  - https://docs.seldon.io/projects/alibi-detect/en/stable/examples/alibi_detect_deploy.html
  - https://github.com/SeldonIO/alibi-detect
  - https://stackoverflow.com/questions/55083642/extract-features-from-last-hidden-layer-pytorch-resnet18
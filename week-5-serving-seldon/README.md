# Serving Model on the Local Kubernetes Cluster with the Seldon

## Setup 

Create kind cluster 

```bash
kind create cluster --name seldon-demo --image=kindest/node:v1.21.2 --config=k8s/kind.yaml
```

## Install Seldon

1. Configure and install `ambassador` as a proxy service


```bash
kubectl apply -f https://github.com/datawire/ambassador-operator/releases/latest/download/ambassador-operator-crds.yaml

kubectl apply -n ambassador -f https://github.com/datawire/ambassador-operator/releases/latest/download/ambassador-operator-kind.yaml

kubectl wait --timeout=180s -n ambassador --for=condition=deployed ambassadorinstallations/ambassador
```

2. Install `seldon core`

```bash
kubectl create namespace seldon-system

helm install seldon-core seldon-core-operator \
    --repo https://storage.googleapis.com/seldon-charts \
    --set usageMetrics.enabled=true \
    --set ambassador.enabled=true \
    --namespace seldon-system
```

3. Make `ambassador` available to the outer world

```bash
kubectl port-forward --address 0.0.0.0 -n ambassador svc/ambassador 8000:80
```

4. Test connection

```bash
kubectl create -f k8s/seldon-iris.yaml
```

Navigate to `http://localhost:8000/seldon/default/iris-model/api/v1.0/doc/` and you have to see the Swagger Docs for the iris model.

```bash
kubectl delete -f k8s/seldon-iris.yaml
```

## Train and Deploy Custom Model

### Install minio

1. Creates a new namespace for the MinIO Tenant.

```bash
kubectl create namespace minio-tenant-1
```

2. Initialize the **Operator**

```bash
kubectl minio init
```

3. Access to the Operator Console:

Run the following command to create a local proxy to the MinIO Operator Console:

```bash
kubectl minio proxy -n minio-operator
```

4. Configure minio

- User Name: **miniouser**
- Password: **miniopassword**

5. Start port forwarding for console to be able to programmatically connect to the minio:

```bash
kubectl port-forward service/minio 8080:80 --address='0.0.0.0' -n minio-tenant-1
```

```bash
kubectl port-forward service/mytenant-console 9090:9090 --address='0.0.0.0' -n minio-tenant-1
```

Test connection:

```bash
miniocli admin info local
```


### Train and upload model

```bash
python train-upload.py
```

### Build Docker image

```bash
export ACCESS_KEY=miniouser
export SECRET_KEY=miniopassword
export MINIO_URI="192.168.1.102:8080"

docker build --rm -t seldon-predictor .
docker tag seldon-predictor:latest yevhenk10s/seldon-predictor:latest
docker push yevhenk10s/seldon-predictor:latest
```

Test image with seldon predictor locally:

```bash
docker run -p 5000:5000 -p 9000:9000 --env ACCESS_KEY=${ACCESS_KEY} --env SECRET_KEY=${SECRET_KEY} --env MINIO_URI=${MINIO_URI} yevhenk10s/seldon-predictor:latest
```

```bash
curl -X POST http://0.0.0.0:9000/predict -H "accept: application/json" -H "Content-Type: application/json" -d '{"data":{"ndarray":[[10, 1], [1, 10]]}}'

>>> {"data":{"names":[],"ndarray":[1,0]},"meta":{}}
```

### Make seldon service

```bash
envsubst < k8s/seldon-custom.yaml | kubectl apply -f -  # don't work for some reason
kubectl apply -f k8s/seldon-custom.yaml
```

Visit http://localhost:8000/seldon/default/classifier-sample/api/v1.0/doc/#/ to check swagger docs.

```bash
curl -X POST "http://localhost:8000/seldon/default/classifier-sample/api/v1.0/predictions" -H "accept: application/json" -H "Content-Type: application/json" -d '{"data":{"ndarray":[[10, 1], [1, 10]]}}'
```
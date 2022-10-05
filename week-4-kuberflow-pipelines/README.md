# Kuberflow Pipeline

## Kuberflow Pipeline on Local Kubernetes Cluster

### Start local k8s cluster with `kind`

```bash
kind create cluster --name=local-cluster
```

### Deploying Kubeflow Pipelines

Follow: https://www.kubeflow.org/docs/components/pipelines/v1/installation/standalone-deployment/

```bash
export PIPELINE_VERSION=1.8.5
kubectl apply -k "github.com/kubeflow/pipelines/manifests/kustomize/cluster-scoped-resources?ref=$PIPELINE_VERSION"
kubectl wait --for condition=established --timeout=60s crd/applications.app.k8s.io
kubectl apply -k "github.com/kubeflow/pipelines/manifests/kustomize/env/dev?ref=$PIPELINE_VERSION"
```

Check for status of the cluster:
```bash
kubectl get namespaces
>>> kubeflow             Active   39s
kubectl get all --namespace kubeflow
```

## Public URL

Get the public URL for the Kubeflow Pipelines UI and use it to access the Kubeflow Pipelines UI:

```bash
kubectl get services --namespace kubeflow
```

```
NAME                              TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)             AGE
cache-server                      ClusterIP   10.96.134.166   <none>        443/TCP             23m
controller-manager-service        ClusterIP   10.96.139.135   <none>        443/TCP             23m
metadata-envoy-service            ClusterIP   10.96.141.158   <none>        9090/TCP            23m
metadata-grpc-service             ClusterIP   10.96.205.99    <none>        8080/TCP            23m
minio-service                     ClusterIP   10.96.178.254   <none>        9000/TCP            23m
ml-pipeline                       ClusterIP   10.96.241.67    <none>        8888/TCP,8887/TCP   23m
ml-pipeline-ui                    ClusterIP   10.96.188.166   <none>        80/TCP              23m
ml-pipeline-visualizationserver   ClusterIP   10.96.27.184    <none>        8888/TCP            23m
mysql                             ClusterIP   10.96.236.138   <none>        3306/TCP            23m
workflow-controller-metrics       ClusterIP   10.96.199.168   <none>        9090/TCP            23m
```

So, we see that `ml-pipeline-ui` is on port 80:

```bash
kubectl port-forward service/ml-pipeline-ui 8000:80 -n kubeflow
```

At the moment on the web UI `localhost:8000` you'll see `Error: failed to retrieve list of pipelines.` error, because there are no pipelines created yet.


Delete local cluster after you're done:

```bash
kubectl delete all --all --all-namespaces
kind delete cluster --name=local-cluster
```

## Training on the Local Kubernetes Cluster

### Build and push Dataset Downloader Docker Image

```bash
cd load-data
docker build --rm -t datadownloader .
docker tag datadownloader:latest yevhenk10s/datadownloader:latest
docker push yevhenk10s/datadownloader:latest
```

### Build and push Trainig Docker Image

```bash
cd train-model
docker build --rm -t trainonkuber .
docker tag trainonkuber:latest yevhenk10s/trainonkuber:latest
docker push yevhenk10s/trainonkuber:latest
```

### Build and push Model Handler Docker Image

```bash
cd artifact-handler
docker build --rm -t artifacthandler .
docker tag artifacthandler:latest yevhenk10s/artifacthandler:latest
docker push yevhenk10s/artifacthandler:latest
```

### Start the cluster

```bash
minikube start  --cpus=4 --memory=10Gi
```

### Enable GPU [FAILED TO MAKE IT WORK]

Follow:
- https://github.com/kubeflow/examples/blob/master/demos/simple_pipeline/demo_setup/README.md
- https://stackoverflow.com/questions/67743158

```bash
docker pull nvidia/k8s-device-plugin:1.9
kubectl create -f https://raw.githubusercontent.com/NVIDIA/k8s-device-plugin/v0.12.3/nvidia-device-plugin.yml
```

### Deploying Kubeflow Pipelines

Follow the previous [section](#deploying-kubeflow-pipelines)

### Port forward for Web UI

```bash
kubectl port-forward service/ml-pipeline-ui 8000:80 -n kubeflow
kubectl port-forward service/ml-pipeline-ui 8888:80 -n kubeflow
```

Default login and password for minio are:

```
accesskey: minio
secretkey: minio123
```

### Compile pipline

```bash
python pipeline.py
```

### Pull big images

For some reason `minikube` [fails](https://github.com/kubernetes/minikube/issues/14806) to pull big images. As the workaround use the next recipe:

```bash
minikube ssh docker pull yevhenk10s/datadownloader:latest
minikube ssh docker pull yevhenk10s/trainonkuber:latest
minikube ssh docker pull yevhenk10s/artifacthandler:latest
```

### Set up WandB env vars

```
export WANDB_PROJECT=artifact-storage
export WANDB_API_KEY=****************
```

### Run experiment with the use of Web UI

Navigate to `localhost:8000`, upload `training-pipeline.yaml` and start training.

## Inference on the Local Kubernetes Cluster

### Build and Push Inference Image to the Registry

```bash
cd artifact-handler
docker build --rm -t inference .
docker tag inference:latest yevhenk10s/inference:latest
docker push yevhenk10s/inference:latest
```

### Pull the Image to the Minikube Cluster

```bash
minikube ssh docker pull yevhenk10s/inference:latest
```

### Clean up the cluster

```bash
minikube stop
minikube delete
```

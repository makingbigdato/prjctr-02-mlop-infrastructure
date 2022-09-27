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

```
NAME                                                   READY   STATUS             RESTARTS        AGE
pod/cache-deployer-deployment-6775db7d9f-ptqbg         1/1     Running            0               23m
pod/cache-server-d9b96559b-zmn7p                       1/1     Running            1 (2m5s ago)    23m
pod/controller-manager-86bf69dc54-9sc2t                1/1     Running            0               23m
pod/metadata-envoy-deployment-d848cdb-pdsvx            1/1     Running            0               23m
pod/metadata-grpc-deployment-784b8b5fb4-knswg          0/1     CrashLoopBackOff   9 (19s ago)     23m
pod/metadata-writer-6447bd6f55-kv7mn                   1/1     Running            5 (3m52s ago)   23m
pod/minio-65dff76b66-fpd9v                             1/1     Running            0               23m
pod/ml-pipeline-685b7b74d-mcw5p                        0/1     CrashLoopBackOff   9 (3m33s ago)   23m
pod/ml-pipeline-persistenceagent-bd9f8d4d7-mqs29       1/1     Running            6 (4m13s ago)   23m
pod/ml-pipeline-scheduledworkflow-544c8bbc58-7558k     1/1     Running            0               23m
pod/ml-pipeline-ui-6c895bb85b-tbllz                    1/1     Running            0               23m
pod/ml-pipeline-viewer-crd-79db74f698-fljql            1/1     Running            0               23m
pod/ml-pipeline-visualizationserver-74fbc54649-f4l4m   1/1     Running            0               22m
pod/mysql-67f7987d45-fx4lh                             1/1     Running            1 (13m ago)     22m
pod/proxy-agent-bff474798-mg9p2                        0/1     Error              8 (5m13s ago)   22m
pod/workflow-controller-594fd96fd5-rpmbz               1/1     Running            0               22m

NAME                                      TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)             AGE
service/cache-server                      ClusterIP   10.96.134.166   <none>        443/TCP             23m
service/controller-manager-service        ClusterIP   10.96.139.135   <none>        443/TCP             23m
service/metadata-envoy-service            ClusterIP   10.96.141.158   <none>        9090/TCP            23m
service/metadata-grpc-service             ClusterIP   10.96.205.99    <none>        8080/TCP            23m
service/minio-service                     ClusterIP   10.96.178.254   <none>        9000/TCP            23m
service/ml-pipeline                       ClusterIP   10.96.241.67    <none>        8888/TCP,8887/TCP   23m
service/ml-pipeline-ui                    ClusterIP   10.96.188.166   <none>        80/TCP              23m
service/ml-pipeline-visualizationserver   ClusterIP   10.96.27.184    <none>        8888/TCP            23m
service/mysql                             ClusterIP   10.96.236.138   <none>        3306/TCP            23m
service/workflow-controller-metrics       ClusterIP   10.96.199.168   <none>        9090/TCP            23m

NAME                                              READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/cache-deployer-deployment         1/1     1            1           23m
deployment.apps/cache-server                      1/1     1            1           23m
deployment.apps/controller-manager                1/1     1            1           23m
deployment.apps/metadata-envoy-deployment         1/1     1            1           23m
deployment.apps/metadata-grpc-deployment          0/1     1            0           23m
deployment.apps/metadata-writer                   1/1     1            1           23m
deployment.apps/minio                             1/1     1            1           23m
deployment.apps/ml-pipeline                       0/1     1            0           23m
deployment.apps/ml-pipeline-persistenceagent      1/1     1            1           23m
deployment.apps/ml-pipeline-scheduledworkflow     1/1     1            1           23m
deployment.apps/ml-pipeline-ui                    1/1     1            1           23m
deployment.apps/ml-pipeline-viewer-crd            1/1     1            1           23m
deployment.apps/ml-pipeline-visualizationserver   1/1     1            1           23m
deployment.apps/mysql                             1/1     1            1           23m
deployment.apps/proxy-agent                       0/1     1            0           23m
deployment.apps/workflow-controller               1/1     1            1           23m

NAME                                                         DESIRED   CURRENT   READY   AGE
replicaset.apps/cache-deployer-deployment-6775db7d9f         1         1         1       23m
replicaset.apps/cache-server-d9b96559b                       1         1         1       23m
replicaset.apps/controller-manager-86bf69dc54                1         1         1       23m
replicaset.apps/metadata-envoy-deployment-d848cdb            1         1         1       23m
replicaset.apps/metadata-grpc-deployment-784b8b5fb4          1         1         0       23m
replicaset.apps/metadata-writer-6447bd6f55                   1         1         1       23m
replicaset.apps/minio-65dff76b66                             1         1         1       23m
replicaset.apps/ml-pipeline-685b7b74d                        1         1         0       23m
replicaset.apps/ml-pipeline-persistenceagent-bd9f8d4d7       1         1         1       23m
replicaset.apps/ml-pipeline-scheduledworkflow-544c8bbc58     1         1         1       23m
replicaset.apps/ml-pipeline-ui-6c895bb85b                    1         1         1       23m
replicaset.apps/ml-pipeline-viewer-crd-79db74f698            1         1         1       23m
replicaset.apps/ml-pipeline-visualizationserver-74fbc54649   1         1         1       22m
replicaset.apps/mysql-67f7987d45                             1         1         1       22m
replicaset.apps/proxy-agent-bff474798                        1         1         0       22m
replicaset.apps/workflow-controller-594fd96fd5               1         1         1       22m

NAME                              TYPE                 VERSION   OWNER   READY   AGE
application.app.k8s.io/pipeline   Kubeflow Pipelines   1.8.5     true            23m
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
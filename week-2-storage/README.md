# Storage and processing of ML data

## Deployment and usage `minio` on `kind`

### Local cluster with `kind`

1. Install `kind`

2. Create local cluster and play around with it

```bash
kind create cluster --name local-cluster
kubectl cluster-info --context kind-local-cluster
kubectl get {nodes|pods|deploy|services}
kind get nodes --name=local-cluster
>>> local-cluster-control-plane
kind get clusters
>>> local-cluster
kind get kubeconfig --name=local-cluster
kind delete cluster --name=local-cluster
```

3. [OPTIONAL] Load your docker image into local cluster (test with well-known web service)

```bash
kind load docker-image yevhenk10s/prjctr02-infrastructure:latest --name=local-cluster

kubectl apply -f ../week-1/.cluster/pod-conf.yaml
kubectl port-forward web-dl 8000:5000
curl localhost:8000
curl -X POST localhost:8000 -H 'Content-Type: application/json' -d '{"texts": ["hello, world", "this is a sentance"]}'
kubectl delete -f ../week-1/.cluster/pod-conf.yaml
```

### Install and initialize `minio`

Main HOWTHO is on the official [README](https://github.com/minio/operator/blob/master/README.md).

1. Install (locally)

```bash
wget -qO- https://github.com/minio/operator/releases/latest/download/kubectl-minio_linux_amd64.zip | bsdtar -xvf- -C ~/.local/bin
chmod +x ~/.local/bin/kubectl-minio
```

2. Verify installation

```bash
kubectl minio version
>>> v4.5.0
```
3. Creates a new namespace for the MinIO Tenant.

```bash
kubectl create namespace minio-tenant-1
```

4. Initialize the **Operator**

```bash
kubectl minio init
```

Check initialization status:

```bash
kubectl get pods -n minio-operator
kubectl get deploy -n minio-operator
kubectl get services -n minio-operator
kubectl get all --namespace minio-operator
```

Wait for all pods (`console` and `minio-operator`) to start.

```bash
kubectl get pods -n minio-operator
```

```
NAME                              READY   STATUS    RESTARTS   AGE
console-78d84698bb-9j9kv          1/1     Running   0          99s
minio-operator-7cdd5b86f8-gnh6q   0/1     Pending   0          99s
minio-operator-7cdd5b86f8-r8w6n   1/1     Running   0          99s
```

4. Access to the Operator Console:

Run the following command to create a local proxy to the MinIO Operator Console:

```bash
kubectl minio proxy -n minio-operator
```

Configure minio and save [setting](https://docs.min.io/minio/k8s/tenant-management/deploy-minio-tenant.html), crate a **Tenant**. You'll get credential on web UI while saving config.

Tenant config:
* Setup
  - name: **mytenant**
  - namespace: **minio-tenant-1**  <-- this was given when a new kubernetes namespace was created `kubectl create namespace minio-tenant-1`
  - number of servers: **1**
  - drives per server: **1**
  - total size: **1Gi**
* Security
  - TLS: **OFF** (necessary to be able to connect locally)
  - AutoCert: **OFF** (necessary to be able to connect locally)

Security if **off** because I didn't manage to properly configure certificates: there are no well detailed documentation of how to do it properly especially on `kind` local cluster.

Wait for the cluster to pull all necessary dependencies. The button `Console` will become active.

Now, the server is running with the following command in a background:

```bash
ps -aux | grep "minio server"
>>> minio server --certs-dir /tmp/certs --console-address :9090
```

Check the status of `minio-tenant-1` namespace:

```bash
kubectl get all --namespace minio-tenant-1
```

Go to created tenant, press `Console` button. Then `Identity` --> `Users` and create new user that will have access to the tenant, for example:
- User Name: **miniouser**
- Password: **miniopassword**
- Policies:
  - consoleAdmin
  - diagnostics
  - readwrite

### Connect to `minio` from Python or console.

Use an example provided in the [documentation](https://docs.min.io/docs/python-client-quickstart-guide.html).

1. Check ports `minio` and `console` are running on:

```bash
kubectl get service --namespace minio-tenant-1
```

You'll get result similar to the following:

```
NAME                      TYPE           CLUSTER-IP      EXTERNAL-IP   PORT(S)          AGE
minio                     LoadBalancer   10.96.30.21     <pending>     80:30159/TCP     10m
mytenant-console          LoadBalancer   10.96.96.214    <pending>     9090:30846/TCP   10m
mytenant-hl               ClusterIP      None            <none>        9000/TCP         10m
mytenant-log-hl-svc       ClusterIP      None            <none>        5432/TCP         9m11s
mytenant-log-search-api   ClusterIP      10.96.221.207   <none>        8080/TCP         9m11s
```

According to the [documentation](https://docs.min.io/minio/k8s/tenant-management/deploy-minio-tenant.html) (right on the bottom of the page):
- The `minio` service corresponds to the MinIO Tenant service. Applications should use this service for performing operations against the MinIO Tenant.
- The `*-console` service corresponds to the [MinIO Console](https://github.com/minio/console). Administrators should use this service for accessing the MinIO Console and performing administrative operations on the MinIO Tenant.

So, let's interrupt Minio Operator web UI (currently running on localhost:9090 according to `kubectl minio proxy -n minio-operator` command we've executed earlier) by terminating port-forwarding. We use it only for initilal cluster set up and tenant creation.

2. Start port forwarding for console to be able to programmatically connect to the minio:

```bash
kubectl port-forward service/minio 8080:80 -n minio-tenant-1
```

```bash
kubectl port-forward service/mytenant-console 9090:9090 -n minio-tenant-1
```

3. Test connection

- `mc` (follow the instructions for [installation](https://docs.min.io/minio/baremetal/reference/minio-mc.html))
  - configure `~/.mc/config.json` file and add the following content:
    
```json
{
	"version": "10",
	"aliases": {
		"local": {
			"url": "http://localhost:8080",
			"accessKey": "miniouser",
			"secretKey": "miniopassword",
			"api": "S3v4",
			"path": "auto"
		}
	}
}
```
    `accessKey` and `secretKey` are just login and password of the user created for the tenant earlier
  - run `miniocli admin info local` to test connection, the output will may look like the following:
    ```
    ●   localhost:8080
        Uptime: 37 minutes 
        Version: 2022-09-07T22:25:02Z
        Network: 1/1 OK 
        Drives: 1/1 OK 
        Pool: 1

    Pools:
        1st, Erasure sets: 1, Disks per erasure set: 1

    1 drive online, 0 drives offline
    ```
  
  - run `file_uploader.py` with a given credentials, the output will may look like the following:
    ```
    Bucket 'dataset' already exists
    './file_uploader.py' is successfully uploaded as object 'file_uploader.py' to bucket 'dataset'.
    ```

## YAML way of deployment

Please, see the reference: https://github.com/kubernetes/examples/tree/master/staging/storage/minio


## Parallelization benchmarking

### Data Set

Data Set is available on the Kaggle [competition](https://www.kaggle.com/competitions/commonlitreadabilityprize/overview).

### Data Set Integration

Download `train.csv` files from Kaggle competition site and put the file in the `./dataset` folder.

### Benchmarking Summary

```
Number of cpus                      : 8
Dataset len                         : 2834

[Single Process] Preprocessing      : 00:00:05
[Single Process] Inference          : 00:01:56
[Single Process] Total              : 00:02:02

[Multiple Processes] Preprocessing  : 00:00:01
[Multiple Processes] Inference      : 00:01:52
[Multiple Processes] Total          : 00:01:53
```

### Conclusion

For the current setup and amount of data the bottleneck of the pipeline is the inference stage, not the data preprocessing stage.

## DVC Setup with MinIO support

1. Install DVC with PIP:

```bash
pip install dvc dvc-s3
```

2. Initilalize DVC

```bash
dvc init
```

3. Add dataset to DVC

```bash
dvc add week-2-storage/dataset
```

4. Add to git updated files

```bash
git add week-2-storage/dataset.dvc week-2-storage/.gitignore
git commit -m "Add raw data"
```

5. Configure DVC to work with MinOI

**It is NOT SECURE** to store secrets in the repo. It is done for educational purposes only!

```bash
dvc remote add -d minio s3://dataset -f
dvc remote modify minio secret_access_key miniopassword
dvc remote modify minio access_key_id miniouser
dvc remote modify minio endpointurl http://localhost:8080
git add .dvc/config
git commit -m "Configure remote storage"
```

6. Push dataset to the minio service

```bash
dvc push
```

7. Push all changes to git

```bash
git push
```

8. [OPTIONAL] Check if dvc pushed dataset to the minio server

```bash
mc ls local
mc ls local/dataset
```

### References:
- https://dvc.org/doc/start/data-management
- https://stackoverflow.com/questions/67635688/installation-dvc-on-minio-storage


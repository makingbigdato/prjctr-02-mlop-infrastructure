# Airflow For Training and Inference Pipeline Management

## Airflow Installation

Follow the [instructions](https://airflow.apache.org/docs/apache-airflow/stable/start.html) to install standalone airflow.

```bash
# Airflow needs a home. `~/airflow` is the default, but you can put it
# somewhere else if you prefer (optional)
export AIRFLOW_HOME=$(pwd)/airflow-home

# Install Airflow using the constraints file
AIRFLOW_VERSION=2.4.1
PYTHON_VERSION="$(python --version | cut -d " " -f 2 | cut -d "." -f 1-2)"
# For example: 3.7
CONSTRAINT_URL="https://raw.githubusercontent.com/apache/airflow/constraints-${AIRFLOW_VERSION}/constraints-${PYTHON_VERSION}.txt"
# For example: https://raw.githubusercontent.com/apache/airflow/constraints-2.4.1/constraints-3.7.txt
pip install "apache-airflow==${AIRFLOW_VERSION}" --constraint "${CONSTRAINT_URL}"

# The Standalone command will initialise the database, make a user,
# and start all components for you.
airflow standalone
```

Local credentials are:

```
Login with username: admin
password is located in: $(AIRFLOW_HOME)/standalone_admin_password.txt
```

Visit localhost:8080 in the browser and use the admin account details shown on the terminal to login.


## Configure and Start Kubernetes Cluster

1. Start kubernetes cluster

```bash
minikube start --cpus=4 --memory=10Gi
```

2. Install `kfp` to create and manage kubeflow pipelines

```bash
pip install kfp
```

3. Install Apache Kubernetes Provider

```bash
pip install apache-airflow-providers-cncf-kubernetes
```

4. Attach volumes to the cluster

For more info follow the [documentation](https://kubernetes.io/docs/tasks/configure-pod-container/configure-persistent-volume-storage/).


```bash
kubectl apply -f airflow-volumes.yaml
```

## Install PostgreSQL

Follow the [instructions](https://wiki.archlinux.org/title/PostgreSQL) to install PostgreSQL and init database.

Follow the [instructions](https://medium.com/geekculture/apache-airflow-2-0-complete-installation-with-wsl-explained-71a65d509aba) to configure PostgreSQL.

Then, init airflow database:

```bash
airflow db init
```

## Add Secrets to the Airflow

Navigate: `Admin` --> `Variables` and add `WANDB_API_KEY` with `WANDB_PROJECT`.


## Run DAGs

With the use of Airflow UI start the configured DAGs.
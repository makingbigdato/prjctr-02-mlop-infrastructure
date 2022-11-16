# Model Monitoring

## Cluster setup

Create cluster with custom config (required for interaction between kind and ambassador):
```bash
kind create cluster --name model-monitoring --image=kindest/node:v1.21.2 --config=k8s/kind.yaml
```

## PR1. Seldon model monitoring

### Prepare Infrastructure

1. Install ambassador

```bash
kubectl apply -f https://github.com/datawire/ambassador-operator/releases/latest/download/ambassador-operator-crds.yaml

kubectl apply -n ambassador -f https://github.com/datawire/ambassador-operator/releases/latest/download/ambassador-operator-kind.yaml

kubectl wait --timeout=180s -n ambassador --for=condition=deployed ambassadorinstallations/ambassador
```

2. Configure namespaces

```bash
kubectl create namespace seldon-system

kubectl create namespace seldon
```

3. Install seldon

```bash
helm install seldon-core seldon-core-operator \
    --repo https://storage.googleapis.com/seldon-charts \
    --set usageMetrics.enabled=true \
    --set ambassador.enabled=true \
    --namespace seldon-system
```

4. Install seldon analytics

```bash
helm install seldon-core-analytics seldon-core-analytics --repo https://storage.googleapis.com/seldon-charts --namespace seldon-system
```

5. Expose services (ambassador, graphana, prometeus)

```bash
kubectl port-forward --address 0.0.0.0 -n ambassador svc/ambassador 8000:80

kubectl port-forward --address 0.0.0.0 -n seldon-system svc/seldon-core-analytics-grafana 3000:80

kubectl port-forward --address 0.0.0.0 -n seldon-system svc/seldon-core-analytics-prometheus-seldon 5000:80
```

Visit `http://localhost:3000/` to see graphana UI. Default login and password for graphana are `admin` and `password`.

Visit `http://localhost:5000/` to see the UI of the Prometeus.

### Prepare Codebase

For more details about available methods see the [docs](https://docs.seldon.io/projects/seldon-core/en/latest/python/python_component.html).

#### Metrics configuration example
For `send_feedback()` function see:
- https://docs.seldon.io/projects/seldon-core/en/latest/_modules/seldon_core/user_model.html
- https://docs.seldon.io/projects/seldon-core/en/latest/_modules/seldon_core/seldon_methods.html

For `metrics()` function see:
- https://github.com/SeldonIO/seldon-core/blob/2704bc1bae499f0343b37ec8eef8141d29513814/python/tests/test_metrics.py#L193-L211

Metrics examples and tutorial:
- https://github.com/SeldonIO/seldon-core/tree/master/examples/feedback/reward-accuracy


#### Build docker image

```bash
cd model-monitoring
docker build --rm -t model-monitoring . && \
docker tag model-monitoring:latest yevhenk10s/model-monitoring:latest && \
docker push yevhenk10s/model-monitoring:latest
```

#### Local tests for container

Start the container:

```bash
export WANDB_API_KEY=****

export WANDB_PROJECT=artifact-storage

docker run -p 5555:5000 -p 9999:9000 --env WANDB_API_KEY=${WANDB_API_KEY} --env WANDB_PROJECT=${WANDB_PROJECT} yevhenk10s/model-monitoring:latest
```

Make requests:

```bash
curl -X POST http://0.0.0.0:9999/predict -H "accept: application/json" -H "Content-Type: application/json" -d '{"data":{"ndarray":[[10, 1], [1, 10]]}}'

>>> {"data":{"names":[],"ndarray":[1,0]},"meta":{"metrics":[{"key":"inference_time","type":"GAUGE","value":0.003155778016662225},{"key":"inference_time_dist","type":"TIMER","value":0.003155778016662225},{"key":"true_pos","type":"GAUGE","value":0},{"key":"true_neg","type":"GAUGE","value":0},{"key":"false_pos","type":"GAUGE","value":0},{"key":"false_neg","type":"GAUGE","value":0},{"key":"request_count","type":"COUNTER","value":1}]}}
```

```bash
curl http://0.0.0.0:9999/health/status

>>> {"data":{"names":[],"tensor":{"shape":[2],"values":[0,1]}},"meta":{"metrics":[{"key":"inference_time","type":"GAUGE","value":0.0026717180153355002},{"key":"inference_time_dist","type":"TIMER","value":0.0026717180153355002},{"key":"true_pos","type":"GAUGE","value":0},{"key":"true_neg","type":"GAUGE","value":0},{"key":"false_pos","type":"GAUGE","value":0},{"key":"false_neg","type":"GAUGE","value":0},{"key":"request_count","type":"COUNTER","value":1}]}}
```

```bash
curl localhost:9999/health/ping

>>> pong
```

### Wrap Container into Kubernetes

```bash
kubectl apply -f k8s/deployment.yaml
```

Visit http://0.0.0.0:8000/seldon/default/classifier-sample/api/v1.0/doc/ for swagger docs.

List of available endpoints:
- http://0.0.0.0:8000/seldon/default/classifier-sample/api/v1.0/predictions
- http://0.0.0.0:8000/seldon/default/classifier-sample/api/v1.0/feedback

Test endpoints:

```bash
curl -X POST http://0.0.0.0:8000/seldon/default/classifier-sample/api/v1.0/predictions -H "accept: application/json" -H "Content-Type: application/json" -d '{"data":{"ndarray":[[10, 1], [1, 10]]}}'

>>> {"data":{"names":[],"ndarray":[1,0]},"meta":{"metrics":[{"key":"inference_time","type":"GAUGE","value":0.0016381210007239133},{"key":"inference_time_dist","type":"TIMER","value":0.0016381210007239133},{"key":"true_pos","type":"GAUGE","value":0},{"key":"true_neg","type":"GAUGE","value":0},{"key":"false_pos","type":"GAUGE","value":0},{"key":"false_neg","type":"GAUGE","value":0},{"key":"request_count","type":"COUNTER","value":1}],"requestPath":{"classifier":"yevhenk10s/model-monitoring:latest"}}}
```

```bash
curl -X POST http://0.0.0.0:8000/seldon/default/classifier-sample/api/v1.0/feedback -H "accept: application/json" -H "Content-Type: application/json" -d '{"request": {"data": {"ndarray": [[10, 1], [1, 10]]}}, "truth":{"data": {"ndarray": [0, 1]}}}'

>>> {"data":{"ndarray":[]},"meta":{"metrics":[{"key":"inference_time","type":"GAUGE"},{"key":"inference_time_dist","type":"TIMER"},{"key":"true_pos","type":"GAUGE"},{"key":"true_neg","type":"GAUGE"},{"key":"false_pos","type":"GAUGE"},{"key":"false_neg","type":"GAUGE","value":2.0},{"key":"request_count"}],"requestPath":{"classifier":"yevhenk10s/model-monitoring:latest"}}}
```

Run simple client:
```bash
python client.py
```

### Setting Up Graphana

1. Navigate to http://localhost:3000
2. Navigate `Create` --> `Dashboard`
3. Select `Prometeus` as the data source
4. In the dropdown menu `Metrics` select metrics you've prepared in `Predictor.py`
5. Then press `Apply` and `Save` dashboard


## PR2. Managed model monitoring tool for your model: Example Arize

Follow the documentation and examples:
- https://docs.arize.com/arize/examples/common-model-types
- https://colab.research.google.com/github/Arize-ai/tutorials_python/blob/main/Arize_Tutorials/Model_Types/Arize_Tutorial_Log_Regression_Boston_House_Prices_With_PandasLogger.ipynb
- https://colab.research.google.com/github/Arize-ai/tutorials_python/blob/main/Arize_Tutorials/Model_Types/Arize_Tutorial_Log_Score_Categorical_Breast_Cancer_With_PandasLogger.ipynb


1. Load initial training and validation datasets

```bash
python ../week-4-kuberflow-pipelines/load-data/download-dataset.py --n-samples=300 --noise=0.3 --random-state=0 --out-file=training-dataset.json

python ../week-4-kuberflow-pipelines/load-data/download-dataset.py --n-samples=300 --noise=0.6 --random-state=42 --out-file=validation-dataset.json
```

2. Download pretrained model

```bash
export WANDB_API_KEY=****
export WANDB_PROJECT=artifact-storage
wandb artifact get yevhen-k-team/artifact-storage/model:latest --root .
```

3. Get Arize `API_KEY` and `SPACE_KEY` by navigating to the settings page in your workspace.

Put env vars to `.env` file.

4. Run

```bash
python arize-client-demo.py
```

5. Navigate to https://app.arize.com, open `Models` --> `YOUR-MODEL-NAME`

Wait for a while because:
```
Data will be available in the UI about 10 minutes after it was received.
```

### Get Familiar with Docs

- https://docs.arize.com/arize/examples/logging-to-arize-tutorials
- https://docs.arize.com/arize/product-guides/quickstart/python-real-time


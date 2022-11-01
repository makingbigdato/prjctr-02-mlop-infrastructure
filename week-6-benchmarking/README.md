# Benchmarking

## PR benchmark for your model forward pass

Run:

```bash
make benchmark-forwardpass
```

Results:

```
---------------- benchmark: 2 tests ----------------
Name (time in ms)                     Mean          
----------------------------------------------------
test_benchmark_forwardpass_gpu      6.8554 (1.0)    
test_benchmark_forwardpass_cpu     35.3109 (5.15)   
----------------------------------------------------
```

Test set up:
- CPU: Intel Core i5-8300H CPU @ 2.30GHz x 8
- RAM: 15.5GiB
- GPU: NVIDIA GeForce GTX 1050 Ti
- DRAM: 4096 MiB
- CUDA: 11.7

## PR benchmark for your model API

1. Build docker image with the API

```bash
cd api/
docker build --rm -t bert-api .
docker tag bert-api:latest yevhenk10s/bert-api:latest
docker push yevhenk10s/bert-api:latest
```

2. Test docker image locally

```bash
docker run -p 5000:5000 yevhenk10s/bert-api:latest
curl localhost:5000
curl -X POST localhost:5000 -H 'Content-Type: application/json' -d '{"texts": ["hello, world", "this is a sentance"]}'
```

3. Run test benchmark

```bash
make benchmark-api-local
```

Results:


| Type | Name       | # reqs | # fails   | Avg  | Min | Max   | Med  | req/s  | failures/s |
| ---- | ---------- | ------ | --------- | ---- | --- | ----- | ---- | ------ | ---------- |
| POST | /          | 2200   | 80(3.64%) | 2988 | 424 | 14541 | 2000 | 108.40 | 1.20       |
|      | Aggregated | 2200   | 80(3.64%) | 2988 | 424 | 14541 | 2000 | 108.40 | 1.20       |

Test set up:
- CPU: Intel Core i5-8300H CPU @ 2.30GHz x 8
- RAM: 15.5GiB
- GPU: NVIDIA GeForce GTX 1050 Ti
- DRAM: 4096 MiB
- CUDA: 11.7
- Noisy neighbours: default minikube cluster activity

### Conclusion

API locally deployed with flask and docker on NVIDIA GeForce GTX 1050 Ti (4.0GiB) starts failing at the rate of ~108 req/s.


## PR k8s deployment YAML for your model API

See files [deployment-api.yaml](./k8s/deployment-api.yaml) and [service-api.yaml](./k8s/service-api.yaml)

Test service locally:

```bash
minikube start  --cpus=4 --memory=10Gi
minikube ssh docker pull yevhenk10s/bert-api:latest
kubectl apply -f k8s/service-api.yaml
kubectl port-forward service/nlp-service 8080:80 --address='0.0.0.0' -n default
curl localhost:8080/predict
>>> {"response": "ok", "runtime": "cpu"}

curl -X POST localhost:8080/predict -H 'Content-Type: application/json' -d '{"texts": ["hello, world", "this is a sentance"]}'
>>> {"response": [[0.8008355498313904], [-0.8118988275527954]], "runtime": "cpu"}

minikube stop
minikube delete
```

Alternatively you can test deployment (but first, delete service `kubectl delete -f k8s/service-api.yaml`)

```bash
kubectl apply -f k8s/deployment-api.yaml
kubectl port-forward service/nlp-service 5000:80 --address='0.0.0.0' -n default
curl localhost:5000/predict
>>> {"response": "ok", "runtime": "cpu"}

curl -X POST localhost:5000/predict -H 'Content-Type: application/json' -d '{"texts": ["hello, world", "this is a sentance"]}'
>>> {"response": [[0.8008355498313904], [-0.8118988275527954]], "runtime": "cpu"}
```

## PR k8s deployment YAML for your model UI (Streamlit)

1. Build docker image with the API

```bash
cd streamlit/
docker build --rm -t bert-streamlit .
docker tag bert-streamlit:latest yevhenk10s/bert-streamlit:latest
docker push yevhenk10s/bert-streamlit:latest
```

2. Test docker image locally

```bash
docker run -p 5000:5000 yevhenk10s/bert-streamlit:latest
```

3. Open browser and navigate to `localhost:5000`.

4. See files [deployment-streamlit.yaml](./k8s/deployment-streamlit.yaml) and [service-streamlit.yaml](./k8s/service-streamlit.yaml)

5. Test service locally:

```bash
minikube ssh docker pull yevhenk10s/bert-streamlit:latest
kubectl apply -f k8s/service-streamlit.yaml
kubectl port-forward service/streamlit-service 8080:80 --address='0.0.0.0' -n default
```

6. Navigate to `localhost:8080` to use web ui.


## PR optimizing inference for your model

**NB**: no test on accuracy drop on quantization are done!

### Dynamic Quantization

Run:

```bash
python bert-quntization.py
```

Results:

| Param                  | Value                  |
| ---------------------- | ---------------------- |
| Size (MB)              | 438.016813             |
| Size (MB)              | 181.500229             |
| Original model result  | [[0.7232117056846619]] |
| Quantized model result | [[0.5428504347801208]] |


### Benchmark Before and After Quantization

Run:
```bash
make quantization-benchmark
```

Results:
```
------------------- benchmark: 4 tests -------------------
Name (time in ms)                           Mean          
----------------------------------------------------------
test_benchmark_forwardpass_gpu_uint8      7.9771 (1.0)    
test_benchmark_forwardpass_gpu_orig      14.0005 (1.76)   
test_benchmark_forwardpass_cpu_uint8     28.1482 (3.53)   
test_benchmark_forwardpass_cpu_orig      26.8769 (3.37)   
----------------------------------------------------------
```

### References

- https://pytorch.org/docs/stable/quantization.html
- https://pytorch.org/tutorials/recipes/recipes/dynamic_quantization.html
- https://pytorch.org/tutorials/intermediate/dynamic_quantization_bert_tutorial.html

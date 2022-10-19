benchmark-forwardpass:
	pytest test_benchmark_forwardpass.py --benchmark-columns=mean

benchmark-api-local:
	locust -f test_api_local.py --headless --users 1000 --spawn-rate 100 -H http://localhost:5000

quantization-benchmark:
	pytest test_benchmark_quantization.py --benchmark-columns=mean
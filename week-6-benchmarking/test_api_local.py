import time
from locust import HttpUser, task, between

PAYLOAD = {"texts": ["hello, world"]}


class QuickstartUser(HttpUser):
    # wait_time = between(1, 5)

    @task
    def post_request(self):
        self.client.post("/predict", json=PAYLOAD)
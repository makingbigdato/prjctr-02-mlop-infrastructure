import requests
from seldon_core.seldon_client import SeldonClient


DOMAIN = "localhost"
AMBASSADOR_PORT = "8000"
MODEL = "classifier-sample"

PREDICT_URL = f"http://{DOMAIN}:{AMBASSADOR_PORT}/seldon/default/{MODEL}/api/v1.0/predictions"
FEEDBACK_URL = f"http://{DOMAIN}:{AMBASSADOR_PORT}/seldon/default/{MODEL}/api/v1.0/feedback"


def send_request_sync():
    data = {"data": {"ndarray": [[10, 1]] * 128}}
    res = requests.post(PREDICT_URL, json=data)
    print(res)
    print(res.json())


def send_feedback_sync():
    data = {"request": {"data": {"ndarray": [[10, 1]]}}, "truth": {"data": {"ndarray": [1]}}}
    res = requests.post(FEEDBACK_URL, json=data)
    print(res)
    print(res.json())


if __name__ == "__main__":
    for _ in range(1000):
        send_request_sync()

    for _ in range(1000):
        send_feedback_sync()

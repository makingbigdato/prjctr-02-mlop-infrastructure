import requests


SELDON_HOST = "http://localhost"
SELDON_PORT = "8000"
SELDON_ENDPOINT = "/seldon/default/classifier-sample/api/v1.0/predictions"

URI = f"{SELDON_HOST}:{SELDON_PORT}{SELDON_ENDPOINT}"

PAYLOAD = {"data":{"ndarray":[[10, 1], [1, 10]]}}

HEADERS = {
    "accept": "application/json",
    "Content-Type": "application/json"
}

PREDICTOR = "yevhenk10s/seldon-predictor:latest"


def test_connection():
    r = requests.post(URI, json=PAYLOAD, headers=HEADERS)
    r.close()
    assert r.status_code == 200


def test_response_structure():
    r = requests.post(URI, json=PAYLOAD, headers=HEADERS)
    r.close()
    response = r.json()
    assert "data" in response.keys()
    assert "names" in response["data"].keys()
    assert "ndarray" in response["data"].keys()
    assert "meta" in response.keys()


def test_response_rediction_len():
    r = requests.post(URI, json=PAYLOAD, headers=HEADERS)
    r.close()
    payload_len = len(PAYLOAD["data"]["ndarray"])
    response = r.json()
    response_len = len(response["data"]["ndarray"])
    assert payload_len == response_len


def test_predictor():
    r = requests.post(URI, json=PAYLOAD, headers=HEADERS)
    r.close()
    response = r.json()
    predictor = response["meta"]["requestPath"]["classifier"]
    assert predictor == PREDICTOR
from fastapi.testclient import TestClient
import numpy as np

from app import app


client = TestClient(app)


def test_app_get():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_app_post():
    response = client.post("/", json={"texts": ["hello, world", "this is a sentance"]})
    assert response.status_code == 200
    results = response.json()["results"]
    assert len(results) == 2
    assert np.isclose(results[0],  0.8008365035057068, atol=1e-5)
    assert np.isclose(results[1], -0.8118982315063477, atol=1e-5)

from model import DummyModel
from flask import Flask, request, jsonify
import json


model = DummyModel()
app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def process():
    if request.method == 'GET':
        return jsonify(response="ok")
    else:
        texts = request.json["texts"]
        response = model.process(texts)
        return jsonify(response=response)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

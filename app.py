from model import DummyModel
from flask import Flask, request, Response
import json


model = DummyModel()
app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def process():
    if request.method == 'GET':
        return Response(response=json.dumps({"response": "ok"}), status=200, mimetype="application/json")
    else:
        texts = request.json["texts"]
        response = model.process(texts)
        return Response(response=json.dumps({"response": response}), status=200, mimetype="application/json")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

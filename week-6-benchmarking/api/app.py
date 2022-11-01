import torch
from model import RegressionModel
from transformers import BertTokenizer
from flask import Flask, request, Response
import json


def init_model():
    model = RegressionModel(device: torch.device)
    model.load_state_dict(torch.load("./weights/bert-base-uncased-regression-weights.pth"))
    model.to(device)
    tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
    model.eval()
    return model, tokenizer


# initialize global vars
device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
print(f">>> using device: {device}")
model, tokenizer = init_model(device)
app = Flask(__name__)


def inference(request):
    texts = request.json["texts"]
    tokens = tokenizer(texts, return_tensors='pt', padding=True)
    input_ids = tokens["input_ids"].to(device)
    token_type_ids = tokens["token_type_ids"].to(device)
    attention_mask = tokens["attention_mask"].to(device)
    tokens = {
        "input_ids": input_ids,
        "token_type_ids": token_type_ids,
        "attention_mask": attention_mask
    }
    with torch.no_grad():
        response = model(tokens).cpu().numpy().tolist()
    return Response(response=json.dumps({"response": response, "runtime": str(device)}), status=200, mimetype="application/json")


@app.route('/predict', methods=['GET', 'POST'])
def process():
    if request.method == 'GET':
        return Response(response=json.dumps({"response": "ok", "runtime": str(device)}), status=200, mimetype="application/json")
    else:
        return inference(request)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

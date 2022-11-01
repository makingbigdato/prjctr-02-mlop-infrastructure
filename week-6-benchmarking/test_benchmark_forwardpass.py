from typing import List, Text, Tuple
import torch
from api.model import RegressionModel
from transformers import BertTokenizer
import gdown
from pathlib import Path
import os


MODEL_URL = "https://drive.google.com/file/d/1M5SFB5cYS7Q3oLpkEQVGERXtquwPxury/view?usp=sharing"
MODEL_SAVE_PATH = "./weights/bert-base-uncased-regression-weights.pth"


def init_model() -> Tuple[torch.nn.Module, torch.nn.Module, torch.device]:
    folder = Path("./weights")
    weights = Path(MODEL_SAVE_PATH)
    if not folder.exists():
        os.mkdir("./weights")
    if not weights.exists():
        gdown.download(
            fuzzy=True, 
            url=MODEL_URL,
            output=MODEL_SAVE_PATH)
    device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
    print(f">>> using device: {device}")
    model = RegressionModel()
    model.load_state_dict(torch.load(MODEL_SAVE_PATH))
    model.to(device)
    tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
    model.eval()
    return model, tokenizer, device


model, tokenizer, _ = init_model()
sentances = ["hello, world"]
device_cpu = torch.device("cpu")
device_gpu = torch.device("cuda")


def inference(sentances: List[Text], device: torch.device):
    tokens = tokenizer(sentances, return_tensors='pt', padding=True)
    input_ids = tokens["input_ids"].to(device)
    token_type_ids = tokens["token_type_ids"].to(device)
    attention_mask = tokens["attention_mask"].to(device)
    tokens = {
        "input_ids": input_ids,
        "token_type_ids": token_type_ids,
        "attention_mask": attention_mask
    }
    with torch.no_grad():
        _ = model(tokens).cpu().numpy().tolist()


def test_benchmark_forwardpass_cpu(benchmark):
    model.to(device=device_cpu)
    benchmark(inference, sentances, device_cpu)


def test_benchmark_forwardpass_gpu(benchmark):
    model.to(device=device_gpu)
    benchmark(inference, sentances, device_gpu)
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


def inference(sentances: List[Text], model: torch.nn.Module, device: torch.device):
    model.to(device=device)
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
        result = model(tokens).cpu().numpy().tolist()
    return result


def print_size_of_model(model):
    torch.save(model.state_dict(), "temp.p")
    print('Size (MB):', os.path.getsize("temp.p")/1e6)
    os.remove('temp.p')


if __name__ == "__main__":
    model, tokenizer, _ = init_model()
    sentances = ["hello, world"]
    device_cpu = torch.device("cpu")
    device_gpu = torch.device("cuda")

    # create a quantized model instance
    model.to(device_cpu)
    model_int8 = torch.quantization.quantize_dynamic(
        model,  # the original model
        {torch.nn.LSTM, torch.nn.Linear},  # a set of layers to dynamically quantize
        dtype=torch.qint8)  # the target dtype for quantized weights

    # check the model size
    print_size_of_model(model)
    print_size_of_model(model_int8)

    # run the model
    result = inference(sentances=sentances, model=model, device=device_cpu)
    print(f"original model result: {result}")

    result = inference(sentances=sentances, model=model_int8, device=device_cpu)
    print(f"quantized model result: {result}")

    # save quantized model
    model_int8.to(device_cpu)
    torch.save(model_int8.state_dict(), './weights/bert-base-uncased-regression-weights-uint8.pth')



    

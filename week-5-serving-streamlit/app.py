import os
from typing import List, Text, Tuple
from pathlib import Path
import torch
from transformers import BertTokenizer
from model import RegressionModel
import gdown
import streamlit as st


MODEL_URL = "https://drive.google.com/file/d/1M5SFB5cYS7Q3oLpkEQVGERXtquwPxury/view?usp=sharing"
MODEL_SAVE_PATH = "./weights/bert-base-uncased-regression-weights.pth"


@st.cache
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


@st.cache
def inference(
    texts: List[Text], 
    model: torch.nn.Module,
    tokenizer: torch.nn.Module,
    device: torch.device) -> List[Text]:

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
    return response


def main():
    model, tokenizer, device = init_model()
    st.title('Pretrained model demo')
    text = st.text_input('Your text:')
    pressed = st.button('Get text score')
    if pressed:
        st.write('Calculating results...')
        result = inference([text], model, tokenizer, device)
        for r in result:
            st.write(f"The score: {r[0]:.2f}")


if __name__ == "__main__":
    main()

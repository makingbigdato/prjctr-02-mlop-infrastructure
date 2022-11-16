from pathlib import Path
import torch
from fastapi import FastAPI, File, UploadFile

from utils import init_model, inference 
from model import CrackClassifierModel

DEVICE: torch.device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")

model = init_model(Path("./weights/model.pth"), model_class=CrackClassifierModel, device=DEVICE)

app = FastAPI()


@app.post("/predict")
async def inference_response(file: UploadFile = File(...)):
    contents = await file.read()
    result = inference(contents, model, DEVICE)
    return {"class": result}


@app.get("/status", status_code=200)
def status():
    return {"status": "ok"}

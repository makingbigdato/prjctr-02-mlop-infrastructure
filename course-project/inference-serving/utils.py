import io
import os
from pathlib import Path
from typing import List

from minio import Minio
import torch
from torchvision import transforms
from PIL import Image

from model import CrackClassifierModel


__all__ = [
    "init_model",
    "inference"
]


ENDPOINT = os.environ["ENDPOINT"]
ACCESS_KEY = os.environ["ACCESS_KEY"]
SECRET_KEY = os.environ["SECRET_KEY"]
CLIENT: Minio = Minio(
    endpoint=ENDPOINT,
    access_key=ACCESS_KEY,
    secret_key=SECRET_KEY,
    secure=False,
    )

def init_model(
    model_path: Path,
    model_class: CrackClassifierModel,
    device: torch.device) -> torch.nn.Module:
    
    if (not model_path.exists()) or (not os.path.isfile(model_path)):
        __download_model(to=model_path)


    model = model_class()
    model.load_state_dict(torch.load(model_path))
    model.to(device)
    model.eval()
    return model


def inference(image: bytes, model: torch.nn.Module, device: torch.device) -> str:
# def inference(image: str, model: torch.nn.Module) -> str:
    image = Image.open(io.BytesIO(image)).convert('RGB')
    # image = Image.open(image).convert('RGB')
    transform=transforms.Compose([
        transforms.Resize(224),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406],
                             std=[0.229, 0.224, 0.225])
    ])
    image = transform(image).unsqueeze(0).to(device)
    prediction = torch.argmax(
        torch.softmax(model(image), dim=1)
        ).item()
    label = "neg" if prediction == 0 else "pos"
    return label



def __download_model(to: Path) -> None:
    model_objects = CLIENT.list_objects("model")
    model_names = [obj.object_name for obj in model_objects]
    latest_model_name = __get_lateset(model_names)
    latest_modle = CLIENT.fget_object(bucket_name="model", object_name=latest_model_name, file_path=str(to))


def __get_lateset(names: List[str]) -> str:
    latest = sorted(names, reverse=True)
    print(latest[0])
    return latest[0]

# if __name__ == "__main__":
#     model = init_model(Path("./weights/model.pth"), model_class=CrackClassifierModel, device=torch.device("cpu"))
#     image_path = "./16001.jpg"
#     inference(image_path, model=model)

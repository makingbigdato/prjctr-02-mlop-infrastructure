import copy
from pathlib import Path
import time
import uuid
from typing import Dict, Tuple
from torchvision import transforms
from torch.utils.data import DataLoader
import torch
from dataset import CrackDataset
from model import CrackClassifierModel
from aim import Run, Repo


# TODO: refactor hardcoded address
repo = Repo(path="aim://192.168.1.104:53800")
aim_run = Run(repo=repo)


DEVICE: torch.device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
BATCH_SIZE = 32
print(f"Using device {DEVICE}")

RAND_UUID = str(uuid.uuid4())
TIMESTR = time.strftime("%Y.%m.%d-%H.%M.%S")
EXPERIMENT_ID = f"{TIMESTR}-{RAND_UUID}"

aim_run["params"] = {
    "device": str(DEVICE),
    "batch_size": BATCH_SIZE,
    "learning_rate": 1e-3,
    "experiment_id": EXPERIMENT_ID,
}


def step(
    model: torch.nn.Module, 
    dataset: Dict[str, torch.utils.data.DataLoader],
    device: torch.device,
    optimizer: torch.optim.Optimizer, 
    criterion: torch.nn.Module,
    batch_size: int,
    phase: str,
    epoch: int) -> Tuple[torch.tensor, torch.tensor, torch.nn.Module]:

    model.to(device=device)

    if phase == "train":
        model.train()  # Set model to training mode
    else:
        model.eval()   # Set model to evaluate mode

    running_loss = 0.0
    running_corrects = 0

    # Iterate over data.
    for batch_idx, item in enumerate(dataset[phase]):
        imgs = item["image"]
        labels = item["label"]
        imgs = imgs.to(device)
        labels = labels.to(device)

        # zero the parameter gradients
        optimizer.zero_grad()

        # forward
        # track history if only in train
        with torch.set_grad_enabled(phase == "train"):
            outputs = model(imgs)
            # preds_sigm = torch.sigmoid(outputs)
            _, preds = torch.max(outputs, 1)
            loss = criterion(outputs, labels)
            # backward + optimize only if in training phase
            if phase == "train":
                loss.backward()
                optimizer.step()

        # statistics
        running_loss += loss.item() * imgs.size(0)
        running_corrects += torch.sum(preds == labels.squeeze().data)
        if batch_idx % 10 == 0 and batch_idx != 0:
            aim_run.track(
                running_loss / (batch_idx*batch_size), name="loss", 
                step=batch_idx*batch_size, 
                epoch=epoch, context={"subset": phase})
            aim_run.track(
                running_corrects / (batch_idx*batch_size), name="acc", 
                step=batch_idx*batch_size, 
                epoch=epoch, context={"subset": phase})

    num_samples = len(dataset[phase]) * batch_size
    epoch_loss = running_loss / num_samples
    epoch_acc = running_corrects.double() / num_samples

    print(f"{phase} Loss: {epoch_loss:.4f} Acc: {epoch_acc:.4f}")
    return epoch_acc, epoch_loss, model



def train_loop(
    model: torch.nn.Module, 
    dataset: Dict[str, torch.utils.data.DataLoader],
    criterion: torch.nn.Module,
    optimizer: torch.optim.Optimizer,
    epochs: int = 5,
    batch_size: int = BATCH_SIZE,
    device: torch.device = DEVICE) -> torch.nn.Module:

    since = time.time()

    best_model_wts = copy.deepcopy(model.state_dict())
    best_acc = 0.0

    for epoch in range(epochs):
        print(f"Epoch {epoch}/{epochs - 1}")
        print("-" * 10)
        # Each epoch has a training and validation phase
        for phase in ["train", "val"]:
            epoch_acc, epoch_loss, model = step(
                model=model,
                dataset=dataset,
                device=device,
                optimizer=optimizer,
                criterion=criterion,
                batch_size=batch_size,
                phase=phase,
                epoch=epoch,
            )
            # deep copy the model
            if phase == "val" and epoch_acc > best_acc:
                best_acc = epoch_acc
                best_model_wts = copy.deepcopy(model.state_dict())
        print()

    time_elapsed = time.time() - since
    print(f"Training complete in {time_elapsed // 60:.0f}m {time_elapsed % 60:.0f}s")
    print(f"Best val Acc: {best_acc:4f}")

    # load best model weights
    model.load_state_dict(best_model_wts)
    return model


def save_model(model: torch.nn.Module, save_to: Path) -> Path:
    name = "model.pth"
    if not save_to.exists():
        save_to.mkdir(parents=True, exist_ok=True)
    save_path = save_to / (EXPERIMENT_ID + "_" + name)
    torch.save(model.state_dict(), save_path)
    return save_path


def evaluate_model(
    model_path: Path,
    model_class: CrackClassifierModel,
    dataset: Dict[str, torch.utils.data.DataLoader],
    device: torch.device,
    batch_size: int = BATCH_SIZE,
    phase = "test") -> torch.Tensor:

    model = model_class()
    model.load_state_dict(torch.load(model_path))
    model.to(device)
    model.eval()
    running_corrects = 0
    with torch.no_grad():
        for batch_idx, item in enumerate(dataset[phase]):
            imgs = item["image"]
            labels = item["label"]
            imgs = imgs.to(device)
            labels = labels.to(device)
            outputs = model(imgs)
            # preds_sigm = torch.sigmoid(outputs)
            _, preds = torch.max(outputs, 1)
            # statistics
            running_corrects += torch.sum(preds == labels.squeeze().data)

        num_samples = len(dataset[phase]) * batch_size
        test_acc = running_corrects.double() / num_samples

        print(f"{phase} Acc: {test_acc:.4f}")
    
    return test_acc


# python main.py  ../../dataset . 1
def train(dataset_path: Path, save_to: Path, epochs: int) -> None:
    transform=transforms.Compose([
        transforms.RandomCrop(224),
        transforms.RandomHorizontalFlip(),
        transforms.RandomVerticalFlip(),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406],
                             std=[0.229, 0.224, 0.225])
    ])
    dataset_train = CrackDataset(dataset_path, "train", transform)

    dataset_train, dataset_val = torch.utils.data.random_split(
        dataset_train, 
        [int(0.8 * len(dataset_train)), int(0.2 * len(dataset_train))])

    dataloader_train = DataLoader(dataset_train, batch_size=BATCH_SIZE,
                                  shuffle=True, num_workers=0)
    
    dataloader_val = DataLoader(dataset_val, batch_size=BATCH_SIZE,
                                shuffle=True, num_workers=0)
    
    dataset_test = CrackDataset(dataset_path, "test", transform)

    dataloader_test = DataLoader(dataset_test, batch_size=BATCH_SIZE,
                                  shuffle=True, num_workers=0)

    dataset = {
        "train": dataloader_train,
        "val": dataloader_val,
        "test": dataloader_test,
    }

    model = CrackClassifierModel()
    model.to(device=DEVICE)
    optimizer = torch.optim.Adam(model.parameters(), lr=aim_run["params"]["learning_rate"])
    criterion = torch.nn.CrossEntropyLoss()

    aim_run["params"]["epochs"] = epochs

    model = train_loop(
        model=model,
        dataset=dataset,
        criterion=criterion,
        optimizer=optimizer,
        epochs=epochs,
    )
    print("TRAINING DONE")
    model.to(torch.device("cpu"))
    model_path = save_model(model, save_to)
    accuracy = evaluate_model(model_path, CrackClassifierModel, dataset, DEVICE)
    print("TESTING DONE")
    print("DONE")

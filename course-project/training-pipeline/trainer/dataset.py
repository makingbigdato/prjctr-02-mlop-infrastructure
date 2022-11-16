from pathlib import Path
import os
from typing import Optional, Callable
import random
from torch.utils.data import Dataset
import torch
from PIL import Image


class CrackDataset(Dataset):

    def __init__(
        self, root_path: Path = "/tmp/dataset", 
        subset: str = "train", 
        transform: Optional[Callable] = None,
        seed: int = 1337,
        slice: Optional[int] = None):

        random.seed(seed)

        self.root_path = root_path
        self.subset = subset
        self.dataset_path = root_path.absolute() / self.subset
        self.transform = transform

        self.classes = ["pos", "neg"]
        image_names_pos = os.listdir(self.dataset_path / "pos")
        image_names_neg = os.listdir(self.dataset_path / "neg")

        imname_label_pairs_pos = [
            (self.dataset_path / "pos" / name, "pos") for name in image_names_pos
        ]
        imname_label_pairs_neg = [
            (self.dataset_path / "neg" / name, "neg") for name in image_names_neg
        ]
        
        self.dataset = imname_label_pairs_pos + imname_label_pairs_neg
        if isinstance(slice, int):
            self.dataset = self.dataset[:slice]
        self.len = len(self.dataset)
        random.shuffle(self.dataset)

    def __len__(self):
        return self.len

    def __getitem__(self, idx):
        if torch.is_tensor(idx):
            idx = idx.tolist()

        img_name, label = self.dataset[idx]
        image = Image.open(img_name)

        if self.transform:
            image = self.transform(image)

        label = torch.tensor(0) if label == "neg" else torch.tensor(1)
        sample = {'image': image, 'label': label}

        return sample
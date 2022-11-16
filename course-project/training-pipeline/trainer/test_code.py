import os
from pathlib import Path
from typing import List
import torch
from torchvision import transforms
from torch.utils.data import DataLoader

from dataset import CrackDataset
from model import CrackClassifierModel
from trainer import train_loop, save_model, evaluate_model

from conftest import option


class TestCode:
    def setup_class(self):
        self.dataset_path = Path(option.dataset_path)
        self.save_to = Path(option.save_to)
        self.epochs = int(option.epochs)

        self.device: torch.device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
        self.batch_sise = 1
        self.transform = transforms.Compose([
            transforms.RandomCrop(224),
            transforms.RandomHorizontalFlip(),
            transforms.RandomVerticalFlip(),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                std=[0.229, 0.224, 0.225])
        ])
        self.model = CrackClassifierModel()
        self.optimizer = torch.optim.Adam(self.model.parameters())
        self.criterion = torch.nn.CrossEntropyLoss()

        dataset_train = CrackDataset(self.dataset_path, "train", self.transform, slice=10)


        dataset_train, dataset_val = torch.utils.data.random_split(
            dataset_train,
            [int(0.8 * len(dataset_train)), int(0.2 * len(dataset_train))])

        dataloader_train = DataLoader(dataset_train, batch_size=self.batch_sise,
                                    shuffle=True, num_workers=1)
        
        dataloader_val = DataLoader(dataset_val, batch_size=self.batch_sise,
                                    shuffle=True, num_workers=1)
        
        dataset_test = CrackDataset(self.dataset_path, "test", self.transform, slice=10)

        dataloader_test = DataLoader(dataset_test, batch_size=self.batch_sise,
                                    shuffle=True, num_workers=1)

        self.dataset = {
            "train": dataloader_train,
            "val": dataloader_val,
            "test": dataloader_test,
        }
        self.model_files: List[Path] = []
    
    def teardown_class(self):
        for file in self.model_files:
            if os.path.exists(file):
                os.remove(file)

    def test_train_loop(self):
        model = train_loop(self.model, self.dataset, self.criterion, self.optimizer, self.epochs, 1, torch.device("cpu"))
        assert isinstance(model, torch.nn.Module)

    def test_save_model(self):
        model = train_loop(self.model, self.dataset, self.criterion, self.optimizer, self.epochs, 1, torch.device("cpu"))
        # model.to(torch.device("cpu"))
        model_path = save_model(model, self.save_to)
        self.model_files.append(model_path)
        assert isinstance(model_path, Path)
        assert "model.pth" in str(model_path)
        assert model_path.is_file()

    def test_evaluate_model(self):
        model = train_loop(self.model, self.dataset, self.criterion, self.optimizer, self.epochs, 1, torch.device("cpu"))
        # model.to(torch.device("cpu"))
        model_path = save_model(model, self.save_to)
        self.model_files.append(model_path)
        accuracy = evaluate_model(model_path, CrackClassifierModel, self.dataset, self.device, 1, "test")
        assert isinstance(accuracy, torch.Tensor)
        assert 0 <= accuracy.item() <= 1

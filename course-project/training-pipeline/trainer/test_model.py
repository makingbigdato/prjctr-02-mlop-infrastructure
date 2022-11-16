import os
from pathlib import Path
from typing import List
import torch
from torchvision import transforms
from torch.utils.data import DataLoader

from dataset import CrackDataset
from model import CrackClassifierModel
from trainer import train_loop, save_model, evaluate_model, step

from conftest import option


class TestModelTraining:

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
    
    def test_shape(self):
        dataset_train = CrackDataset(self.dataset_path, "train", self.transform, slice=10)
        inputs = torch.randn(size=(4, 3, 224, 224))
        assert self.model(inputs).shape == torch.Size([len(inputs), len(dataset_train.classes)])
    
    def test_batch_overfit(self):
        model = train_loop(
            model=self.model,
            dataset=self.dataset,
            criterion=self.criterion,
            optimizer=self.optimizer,
            epochs=5,
            batch_size=1,
            device=self.device
        )
        model.to(torch.device("cpu"))
        model_path = save_model(model, self.save_to)
        self.model_files.append(model_path)
        accuracy = evaluate_model(model_path, CrackClassifierModel, self.dataset, torch.device("cpu"), 1, "train")
        assert accuracy.item() > 0.99
    
    def test_loss_decrease(self):
        _, epoch_1_loss, model = step(
                model=self.model,
                dataset=self.dataset,
                device=self.device,
                optimizer=self.optimizer,
                criterion=self.criterion,
                batch_size=1,
                phase="train",
                epoch=1,
            )
        _, epoch_2_loss, _ = step(
                model=model,
                dataset=self.dataset,
                device=self.device,
                optimizer=self.optimizer,
                criterion=self.criterion,
                batch_size=1,
                phase="train",
                epoch=1,
            )
        assert epoch_2_loss < epoch_1_loss

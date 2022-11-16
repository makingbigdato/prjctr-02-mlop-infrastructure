import torch
from torchvision import models
from torchvision.models.resnet import ResNet18_Weights


class CrackClassifierModel(torch.nn.Module):

    def __init__(self) -> None:
        super().__init__()
        self.model = models.resnet18(weights=ResNet18_Weights.DEFAULT)
        for param in self.model.parameters():
            param.requires_grad = False
        fc_inputs = self.model.fc.in_features
        self.model.fc = torch.nn.Sequential(
            torch.nn.Linear(fc_inputs, 128),
            torch.nn.ReLU(),
            torch.nn.Dropout(0.4),
            torch.nn.Linear(128, 2)
        )
    
    def forward(self, x: torch.tensor) -> torch.tensor:
        return self.model(x)

from typing import Dict
import torch
from transformers import BertModel


__all__ = ["RegressionModel"]


class RegressionModel(torch.nn.Module):
    """
    Example of Bert feature extraction:
    >>> model = BertModel.from_pretrained("bert-base-uncased")
    >>> tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
    >>> text = ["Replace me by any text you'd like.",
        "Replace me by any text you'd like.", "Replace me by any text you'd like."]
    >>> encoded_input = tokenizer(text, return_tensors='pt', padding=True)
    >>> features = model(**encoded_input)
    >>> features.last_hidden_state.size()
    """

    def __init__(self) -> None:
        super(RegressionModel, self).__init__()
        self.base_model = BertModel.from_pretrained("bert-base-uncased")
        self.base_model.requires_grad_(False)
        self.linear = torch.nn.Linear(768, 1)
        self.linear.requires_grad_(True)

    def forward(self, x: Dict[str, torch.Tensor]) -> torch.Tensor:
        features = self.base_model(**x)
        output = torch.mean(features.last_hidden_state, dim=-2)
        output = self.linear(output)
        return output

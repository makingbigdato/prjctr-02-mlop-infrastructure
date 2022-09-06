from typing import Any, List, Text


__all__ = ["DummyModel"]


class DummyModel():
    """
    Dummy class for DL model
    """

    def __init__(self) -> None:
        super(DummyModel, self).__init__()

    def forward(self, x: Any) -> Text:
        return str(x)

    def process(self, x: List[Text]) -> List[Text]:
        return x

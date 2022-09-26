import pytest
from transformers import pipeline


# Using a specific model for sentiment analysis
@pytest.fixture()
def get_pipeline(pipeline_name: str = "finiteautomata/bertweet-base-sentiment-analysis"):
    model = pipeline(model=pipeline_name)
    return model


@pytest.mark.usefixtures("get_pipeline")
class TestModel:

    def test_invariance_verbs(self, get_pipeline):
        model = get_pipeline
        tokens = ["clarified", "reveiled"]
        texts = [f"The movie is awesome and it {word} the meaning of life" for word in tokens]
        predicts = model(texts)
        assert all([predict["label"] == predicts[0]["label"] for predict in predicts])

    def test_invariance_numbers(self, get_pipeline):
        model = get_pipeline
        tokens = ["42", "-15.2"]
        texts = [f"The movie is garbage and it has the next rating: {num}" for num in tokens]
        predicts = model(texts)
        assert all([predict["label"] == predicts[0]["label"] for predict in predicts])

    def test_directional(self, get_pipeline):
        model = get_pipeline
        tokens = ["masterpiece", "failure"]
        texts = [f"The movie is absolute {token} of the year!" for token in tokens]
        predicts = model(texts)
        assert not all([predict["label"] == predicts[0]["label"] for predict in predicts])

    def test_minimum_functionality_pos(self, get_pipeline):
        model = get_pipeline
        pos_tokens = [
            "good", "healthy", "attractive", "appealing", 
            "best", "ideal", "affordable", 
            "exciting", "great", "excellent",
        ]
        texts = [f"The movie is {token}, nothing to say more" for token in pos_tokens]
        predicts = model(texts)
        assert all([predict["label"] == predicts[0]["label"] for predict in predicts]) and predicts[0]["label"] == "POS"

    def test_minimum_functionality_neg(self, get_pipeline):
        model = get_pipeline
        neg_tokens = [
            "bad", "boring", "terrible", "worst", "unfeasible",
            "unappropriate", "awful", "time-consuming"
        ]
        texts = [f"The movie is {token}, nothing to say more" for token in neg_tokens]
        predicts = model(texts)
        print(predicts)
        assert all([predict["label"] == predicts[0]["label"] for predict in predicts]) and predicts[0]["label"] == "NEG"

from train import get_dataset
import pandas as pd
import great_expectations as ge
import os
import pytest


# create pandas dataset for test set from huggingfaces format
@pytest.fixture()
def init_dataset():
    DATASET_DIR = "./dataset/"
    DATASET_NAME = "imdb.csv"
    if not os.path.exists(DATASET_DIR):
        os.mkdir(DATASET_DIR)
    if not os.path.exists(DATASET_DIR+DATASET_NAME):
        dataset = get_dataset()
        df = pd.DataFrame(dataset["train"])
        df.to_csv(DATASET_DIR+DATASET_NAME, index=False)

    df = pd.read_csv(DATASET_DIR+DATASET_NAME)
    df = ge.from_pandas(df)
    return df


@pytest.mark.usefixtures("init_dataset")
class TestDataset:

    def test_table_columns_to_match_ordered_list(self, init_dataset):
        df = init_dataset
        res = df.expect_table_columns_to_match_ordered_list(column_list=['text', 'label'])
        assert res["success"]

    def test_expect_column_values_to_not_be_null_text(self, init_dataset):
        df = init_dataset
        res = df.expect_column_values_to_not_be_null(column='text')
        assert res["success"]

    def test_expect_column_values_to_be_of_type_text(self, init_dataset):
        df = init_dataset
        res = df.expect_column_values_to_be_of_type(column='text', type_='str')
        assert res["success"]

    def test_expect_column_values_to_not_be_null_label(self, init_dataset):
        df = init_dataset
        res = df.expect_column_values_to_not_be_null(column='label')
        assert res["success"]

    def test_expect_column_values_to_be_of_type_label(self, init_dataset):
        df = init_dataset
        res = df.expect_column_values_to_be_of_type(column='label', type_='int')
        assert res["success"]

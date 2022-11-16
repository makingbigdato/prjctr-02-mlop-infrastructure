import os


def test_dataset_structure_train(dataset_path):
    files = os.listdir(dataset_path)
    assert "train" in files


def test_dataset_structure_test(dataset_path):
    files = os.listdir(dataset_path)
    assert "test" in files


def test_dataset_structure_train_pos(dataset_path):
    files = os.listdir(f"{dataset_path}/train")
    assert "pos" in files


def test_dataset_count_train_pos(dataset_path):
    files = os.listdir(f"{dataset_path}/train/pos/")
    assert len(files) == 16_000


def test_dataset_structure_train_neg(dataset_path):
    files = os.listdir(f"{dataset_path}/train")
    assert "neg" in files


def test_dataset_count_train_neg(dataset_path):
    files = os.listdir(f"{dataset_path}/train/neg/")
    assert len(files) == 16_000


def test_dataset_structure_test_pos(dataset_path):
    files = os.listdir(f"{dataset_path}/test")
    assert "pos" in files


def test_dataset_count_test_pos(dataset_path):
    files = os.listdir(f"{dataset_path}/test/pos/")
    assert len(files) == 4_000


def test_dataset_structure_test_neg(dataset_path):
    files = os.listdir(f"{dataset_path}/test")
    assert "neg" in files


def test_dataset_count_test_neg(dataset_path):
    files = os.listdir(f"{dataset_path}/test/neg/")
    assert len(files) == 4_000
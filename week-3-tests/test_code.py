from train import (
    get_dataset,
    prepare_dataset,
    save_model,
    train,
    inference,
)

import shutil
import os
import torch


class TestDataSetProcessing:

    def test_get_dataset(self):
        imdb = get_dataset("imdb")
        assert imdb is not None

    def test_prepare_dateset(self):
        imdb = get_dataset()
        train_dataset_len = 100
        test_dataset_len = 10
        seed = 42
        train_dataset, test_dataset = prepare_dataset(imdb, train_dataset_len, test_dataset_len, seed)
        assert len(train_dataset) == train_dataset_len and len(test_dataset) == test_dataset_len


class TestTraining:
    
    def setup_method(self):
        self.output_dir = "./test_training/"
        self.train_config = {
            "dataset" : "imdb",
            "n_train" : 10,
            "n_test" : 10,
            "num_train_epochs" : 1,
            "batch_size" : 1,
            "seed" : 42,
            "no_cuda": False,
            "save_strategy": "epoch",
        }
        self.model_files = [
            "config.json",
            "pytorch_model.bin",
            "special_tokens_map.json",
            "tokenizer.json",
            "tokenizer_config.json",
            "training_args.bin",
            "vocab.txt",
        ]

    def teardown_method(self):
        if os.path.exists(self.output_dir):
            shutil.rmtree(self.output_dir)

    def test_train(self):
        trainer, _ = train(self.output_dir, **self.train_config)
        assert trainer is not None and os.path.exists(self.output_dir) and os.path.isdir(self.output_dir)

    def test_save_model(self):
        trainer, _ = train(self.output_dir, **self.train_config)
        save_model(trainer, self.output_dir)
        files = os.listdir(self.output_dir)
        for model_file in self.model_files:
            assert model_file in files

    def test_inference(self):
        trainer, _ = train(self.output_dir, **self.train_config)
        save_model(trainer, self.output_dir)
        sentances = [
            "simple and interesting movie",
            "boring movie with failed casting",
            "movie director is genius, awesome!"
        ]
        n_samples = len(sentances)
        class_set = [0, 1]
        classes, probas = inference(sentances=sentances, pretrain_path=self.output_dir)
        max_item = torch.max(classes).item()
        min_item = torch.min(classes).item()
        assert len(classes) == len(probas) == n_samples
        assert max_item in class_set and min_item in class_set
        for p in probas:
            assert 0 <= p <= 1


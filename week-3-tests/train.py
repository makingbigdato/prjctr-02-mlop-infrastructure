from transformers import AutoTokenizer
from datasets import load_dataset
from transformers import DataCollatorWithPadding
from transformers import AutoModelForSequenceClassification
import numpy as np
from datasets import load_metric
from transformers import TrainingArguments, Trainer
from transformers import pipeline
import argparse
import os
import torch


def get_dataset(dataset="imdb"):
    return load_dataset(dataset)


def prepare_dataset(dataset, n_train, n_test, seed=42):
    train_dataset = dataset["train"].shuffle(seed=seed).select([i for i in list(range(n_train))])
    test_dataset = dataset["test"].shuffle(seed=seed).select([i for i in list(range(n_test))])
    return train_dataset, test_dataset


# Define the evaluation metrics 
def compute_metrics(eval_pred):
    load_accuracy = load_metric("accuracy")
    load_f1 = load_metric("f1")

    logits, labels = eval_pred
    predictions = np.argmax(logits, axis=-1)
    accuracy = load_accuracy.compute(predictions=predictions, references=labels)["accuracy"]
    f1 = load_f1.compute(predictions=predictions, references=labels)["f1"]
    return {"accuracy": accuracy, "f1": f1}


def save_model(trainer, output_dir="./weights"):
    trainer.save_model(output_dir)


def train(output_dir="./weights",
          dataset="imdb",
          n_train=3000,
          n_test=300,
          num_train_epochs=2,
          batch_size=4,
          seed=42,
          no_cuda=False,
          save_strategy="epoch"):
    ### Intial Preparation
    # Load data
    imdb = get_dataset(dataset)

    # Create a smaller training dataset for faster training times
    small_train_dataset, small_test_dataset = prepare_dataset(imdb, n_train=n_train, n_test=n_test, seed=seed)
    
    # print(small_train_dataset[0])
    # print(small_test_dataset[0])

    # Set DistilBERT tokenizer
    tokenizer = AutoTokenizer.from_pretrained("distilbert-base-uncased")

    # Prepare the text inputs for the model
    def preprocess_function(examples):
        return tokenizer(examples["text"], truncation=True)

    tokenized_train = small_train_dataset.map(preprocess_function, batched=True)
    tokenized_test = small_test_dataset.map(preprocess_function, batched=True)

    # Use data_collector to convert our samples to PyTorch tensors and concatenate them with the correct amount of padding
    data_collator = DataCollatorWithPadding(tokenizer=tokenizer)

    ### Train the model

    # Define DistilBERT as our base model:
    model = AutoModelForSequenceClassification.from_pretrained("distilbert-base-uncased", num_labels=2)

    # Define a new Trainer with all the objects we constructed so far

    training_args = TrainingArguments(
        output_dir=output_dir,
        learning_rate=2e-5,
        per_device_train_batch_size=batch_size,
        per_device_eval_batch_size=batch_size,
        num_train_epochs=num_train_epochs,
        weight_decay=0.01,
        save_strategy=save_strategy, 
        push_to_hub=False,
        seed=seed,
        no_cuda=no_cuda,
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_train,
        eval_dataset=tokenized_test,
        tokenizer=tokenizer,
        data_collator=data_collator,
        compute_metrics=compute_metrics,
    )
    
    # Train the model
    training_stats = trainer.train()    
    return trainer, training_stats


def inference(sentances=["I love this movie", "This movie sucks!"], pretrain_path="./weights/"):

    # Set DistilBERT tokenizer
    tokenizer = AutoTokenizer.from_pretrained(os.path.abspath(pretrain_path))
    # Define DistilBERT as our base model:
    model = AutoModelForSequenceClassification.from_pretrained(os.path.abspath(pretrain_path))
    
    # Run inferences with your new model using Pipeline
    with torch.no_grad():
        tokens = tokenizer(sentances, return_tensors='pt', padding=True)
        print(tokens)
        sentiments = model(**tokens)
        predicts = torch.max(torch.sigmoid(sentiments.logits), dim=-1)
        classes = predicts.indices
        probas = predicts.values
    return classes, probas


if __name__ == "__main__":    
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--action', default='train', choices=['train', 'inference'], required=True)

    args = parser.parse_args()

    output_dir = "./weights"
    if args.action == "train":
        trainer, training_stats = train(output_dir)
        # Save the model locally
        save_model(trainer, output_dir)
        # Compute the evaluation metrics
        evals = trainer.evaluate()
        print(evals)
    if args.action == "inference":
        classes, probas = inference()
        print(f"classes: {classes}")
        print(f"probas: {probas}")

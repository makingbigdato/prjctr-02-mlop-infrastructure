from train import get_dataset
import pandas as pd
import os

# create pandas dataset for test from huggingfaces format
DATASET_DIR = "./dataset/"
DATASET_NAME = "imdb.csv"
if not os.path.exists(DATASET_DIR):
    os.mkdir(DATASET_DIR)
if not os.path.exists(DATASET_DIR+DATASET_NAME):    
    dataset = get_dataset()
    df = pd.DataFrame(dataset["train"])
    df.to_csv(DATASET_DIR+DATASET_NAME, index=False)

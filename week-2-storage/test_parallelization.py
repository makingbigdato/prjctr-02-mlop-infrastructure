from typing import Dict, List, Optional, Text, Tuple
import torch
from transformers import BertModel
from transformers import BertTokenizer
import pandas as pd
import nltk
from nltk.corpus import stopwords
import re
from nltk.stem import WordNetLemmatizer
import time
from timeit import default_timer
import os
import gdown
import multiprocessing
import torch.multiprocessing as mp


"""
Brief Summary:
Number of cpus                      : 8
Dataset len                         : 2834
[Single Process] Preprocessing      : 00:00:05
[Single Process] Inference          : 00:01:56
[Single Process] Total              : 00:02:02
[Multiple Processes] Preprocessing  : 00:00:01
[Multiple Processes] Inference      : 00:01:52
[Multiple Processes] Total          : 00:01:53


Ideas for text processing were taken from:
- https://towardsdatascience.com/a-guide-to-cleaning-text-in-python-943356ac86ca
"""


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


def init_model() -> Tuple[torch.nn.Module, torch.nn.Module, torch.device]:
    if not os.path.exists("./weights"):
        os.mkdir("./weights")
    if not os.path.exists("./weights/bert-base-uncased-regression-weights.pth"):
        gdown.download(
            fuzzy=True, 
            url="https://drive.google.com/file/d/1M5SFB5cYS7Q3oLpkEQVGERXtquwPxury/view?usp=sharing",
            output="./weights/bert-base-uncased-regression-weights.pth")
    device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
    print(f">>> using device: {device}")
    model = RegressionModel()
    model.load_state_dict(torch.load("./weights/bert-base-uncased-regression-weights.pth"))
    model.to(device)
    tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
    model.eval()
    return model, tokenizer, device


def text_preprocessing(texts: List[Text], 
        queue: Optional[multiprocessing.Queue]
        ) -> Optional[List[Text]]:
    # make text lowercase
    lower = [t.lower() for t in texts]

    # removing stopwords
    result = []
    for text in lower:
        text = " ".join([word for word in text.split() if word not in stop_words])
        result.append(text)

    # removing URLs, hashtags, punctuation, mentions, etc.
    result = [re.sub("@\S+", "", text) for text in result]
    result = [re.sub("\$", "", text) for text in result]
    result = [re.sub("https?:\/\/.*[\r\n]*", "", text) for text in result]
    result = [re.sub("#", "", text) for text in result]

    # remove punctuation
    result = [re.sub(r'[^\w\s]', '', text) for text in result]

    # lemmatization because why not? usually it is bad idea to train modern NLP models
    # with the use of stemming and lemmatization. so, here we use those techniques 
    # only for performance testing purposes
    lemmatizer = WordNetLemmatizer()
    lemmatized = []
    for text in result:
        text = "".join([lemmatizer.lemmatize(word) for word in text])
        lemmatized.append(text)
    
    if queue:
        queue.put(lemmatized)
    else:
        return lemmatized


def tokeinization(tokenizer: torch.nn.Module, 
        device: torch.device, 
        texts: List[Text], 
        queue: Optional[multiprocessing.Queue]
        ) -> Dict[Text, torch.tensor]:
    tokens = tokenizer(texts, return_tensors='pt', padding=True)
    input_ids = tokens["input_ids"].to(device)
    token_type_ids = tokens["token_type_ids"].to(device)
    attention_mask = tokens["attention_mask"].to(device)
    tokens = {
        "input_ids": input_ids,
        "token_type_ids": token_type_ids,
        "attention_mask": attention_mask
    }
    if queue:
        queue.put(tokens)
    else:
        return tokens


def inference(model: torch.nn.Module, tokens: Dict[Text, torch.tensor], texts: List[Text]) -> None:
    input_ids = tokens["input_ids"]
    token_type_ids = tokens["token_type_ids"]
    attention_mask = tokens["attention_mask"]
    batch_size = 32
    iterations = len(texts)//batch_size
    with torch.no_grad():
        for batch_idx in range(iterations):
            if (len(texts) - iterations*batch_size) >= 0:
                tokens_i = {
                    "input_ids": input_ids[batch_idx*batch_size : (batch_idx+1)*batch_size],
                    "token_type_ids": token_type_ids[batch_idx*batch_size : (batch_idx+1)*batch_size],
                    "attention_mask": attention_mask[batch_idx*batch_size : (batch_idx+1)*batch_size],
                }
            else:
                tokens_i = {
                    "input_ids": input_ids[batch_idx*batch_size : ],
                    "token_type_ids": token_type_ids[batch_idx*batch_size : ],
                    "attention_mask": attention_mask[batch_idx*batch_size : ],
                }
            _result = model(tokens_i).cpu().numpy().tolist()



if __name__ == "__main__":

    nltk.download("stopwords")
    nltk.download('wordnet')
    nltk.download('omw-1.4')
    stop_words = set(stopwords.words("english"))

    model, tokenizer, device = init_model()

    df = pd.read_csv("./dataset/train.csv")
    # Get target column only
    df = df["excerpt"].values.tolist()
    print(len(df))
    
    # Start preprocessing and inference w\o parallelization
    start = default_timer()
    text_preprocessing(df, queue=None)
    elapsed_preproc = default_timer() - start
    print(f"[Single Process] Preprocessing: {time.strftime('%H:%M:%S', time.gmtime(elapsed_preproc))}")

    start = default_timer()
    tokens = tokeinization(tokenizer, device, df)
    inference(model, tokens, df)
    elapsed_inference = default_timer() - start
    print(f"[Single Process] Inference: {time.strftime('%H:%M:%S', time.gmtime(elapsed_inference))}")
    print(f"[Single Process] Total: {time.strftime('%H:%M:%S', time.gmtime(elapsed_inference+elapsed_preproc))}")

    # #### Multiprocessing 

    # Start preprocessing and inference with parallelizaiton
    # (not the best way to architecture multiprocessing in this case)
    cpus = multiprocessing.cpu_count()
    print(f"Number of cpu : {cpus}")

    # Preprocessing
    jobs = []
    queue = multiprocessing.Queue()
    queues = []
    dataset_size = len(df)
    dataset_per_cpu = dataset_size // cpus

    for i in range(cpus):
        start = i*dataset_per_cpu
        end = (i+1)*dataset_per_cpu
        if (dataset_size - end) >= dataset_per_cpu:
            p = multiprocessing.Process(target=text_preprocessing, args=(df[start : end], queue))
            jobs.append(p)
            queues.append(queue)
        else:
            p = multiprocessing.Process(target=text_preprocessing, args=(df[start : ], queue))
            jobs.append(p)
            queues.append(queue)

    start = default_timer()
    [p.start() for p in jobs]
    df_preprocessed = []
    for i in range(cpus):
        df_preprocessed.extend(queues[i].get())
    [p.join() for p in jobs]
    elapsed_preproc = default_timer() - start
    print(len(df_preprocessed))
    print(f"[Multiple Processes] Preprocessing: {time.strftime('%H:%M:%S', time.gmtime(elapsed_preproc))}")

    start = default_timer()
    tokens = tokeinization(tokenizer, device, df, None)
    inference(model, tokens, df)
    elapsed_inference = default_timer() - start
    print(f"[Multiple Processes] Inference: {time.strftime('%H:%M:%S', time.gmtime(elapsed_inference))}")
    print(f"[Multiple Processes] Total: {time.strftime('%H:%M:%S', time.gmtime(elapsed_inference+elapsed_preproc))}")


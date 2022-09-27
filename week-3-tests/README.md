# Testing in ML

Main article: https://madewithml.com/courses/mlops/testing
We'll testing the code/repo:https://huggingface.co/blog/sentiment-analysis-python

## Testing the code

Trainint results:

Seed: 42
```json
{'eval_loss': 0.5422639846801758, 'eval_accuracy': 0.8733333333333333, 'eval_f1': 0.8741721854304636, 'eval_runtime': 10.2807, 'eval_samples_per_second': 29.181, 'eval_steps_per_second': 7.295, 'epoch': 2.0}
```


## Testing the dataset

### Initial Set Up

Follow the instructions on: https://madewithml.com/courses/mlops/testing/#data

Init expectations:

```bash
great_expectations init
```

Attach data source:

```bash
great_expectations datasource new
```

Add new suite (interactively):

```bash
great_expectations suite new
```

Use the docs to add expectations: https://docs.greatexpectations.io/docs/guides/expectations/create_expectations_overview

Check suite list:

```bash
great_expectations suite list
```

If necessary, you can edit your suite:

```bash
great_expectations suite edit <SUITE_NAME>
```

Create new checkpoint (`imdb-checkpoint-1`)

```bash
great_expectations checkpoint new CHECKPOINT_NAME
```

Run testing checkpoint:

```bash
great_expectations checkpoint run CHECKPOINT_NAME
```

### Run Test

1. Initialize data set:

```bash
python init_dataset.py
```

2. Run tests:

```bash
great_expectations checkpoint run imdb-checkpoint-1
```

3. OR Run with pytest

```bash
pytest test_dataset.py
```


#!/usr/bin/env python3

import kfp.dsl as kfp
import os
from kubernetes.client.models import V1EnvVar


WANDB_PROJECT = os.getenv("WANDB_PROJECT")
WANDB_API_KEY = os.getenv("WANDB_API_KEY")


def download_dataset_op(
  name: str = "Dataset Downloading",
  n_samples=200,
  noise=0.3, 
  random_state=0, 
  out_file="dataset.json"):
  return kfp.ContainerOp(
    name=name,
    image="yevhenk10s/datadownloader:latest",
    command=["python3", "/load-data/download-dataset.py"],
    arguments=[
      "--n-samples", n_samples,
      "--noise", noise,
      "--random-state", random_state,
      "--out-file", out_file
    ],
    file_outputs={'dataset': f'/load-data/{out_file}'},
  )


def training_op(
    dataset_path: str,
    name: str = "Test Training",
    scores_path = "scores.json",
    out_model_path = "cls.pekl",
    max_depth = 5,
    n_estimators = 10,
    max_features = 1,
    random_state = 1337):
  return kfp.ContainerOp(
    name=name,
    image='yevhenk10s/trainonkuber:latest',
    command=['python3', '/train-dir/train-pipeline.py'],
    arguments=[
        "--dataset-path", dataset_path,
        "--scores-path", scores_path,
        "--out-model-path", out_model_path,
        "--max-depth", max_depth,
        "--n-estimators", n_estimators,
        "--max-features", max_features,
        "--random-state", random_state
    ],
    file_outputs={
      "scores": f"/train-dir/{scores_path}",
      "model": f"/train-dir/{out_model_path}"
    }
  )

def postprocessing_op(scores,
                      step_name='Get Training Metrics'):
  return kfp.ContainerOp(
    name=step_name,
    image='library/bash:4.4.23',
    command=['sh', '-c'],
    arguments=['echo "%s"' % scores]
  )

def artifact_handler(model_path: str,
                     step_name='Upload Model'):
  handler = kfp.ContainerOp(
    name=step_name,
    image="yevhenk10s/artifacthandler:latest",
    command="python3 handler.py".split(),
    arguments=["--model-path", model_path]
  )
  env_var_project = V1EnvVar(name="WANDB_PROJECT", value=WANDB_PROJECT)
  handler = handler.add_env_variable(env_var_project)
  env_var_password = V1EnvVar(name="WANDB_API_KEY", value=WANDB_API_KEY)
  handler = handler.add_env_variable(env_var_password)
  return handler

@kfp.pipeline(
  name='Training Pipeline Example',
  description='Demonstrate the Kubeflow pipelines SDK without GPUs'
)
def kubeflow_training():
  dataset = download_dataset_op()
  training = training_op(dataset_path=kfp.InputArgumentPath(dataset.outputs["dataset"], path="/load-data/dataset.json"))  # .set_gpu_limit(1)
  handler = artifact_handler(model_path=kfp.InputArgumentPath(training.outputs["model"], path="/train-dir/cls.pekl"))
  postprocessing = postprocessing_op(scores=training.outputs["scores"])

if __name__ == '__main__':
  import kfp.compiler as compiler
  compiler.Compiler().compile(kubeflow_training, "training-pipeline.yaml")
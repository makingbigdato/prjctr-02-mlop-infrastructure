#!/usr/bin/env python3

import kfp.dsl as kfp


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
    output_artifact_paths={'dataset': f'/load-data/{out_file}'},
  )


def training_op(
    dataset_content: str,
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
        "--dataset-content", dataset_content,
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

@kfp.pipeline(
  name='Training Pipeline Example',
  description='Demonstrate the Kubeflow pipelines SDK without GPUs'
)
def kubeflow_training():
  dataset = download_dataset_op()
  training = training_op(dataset_content=dataset.outputs["dataset"])  # .set_gpu_limit(1)
  postprocessing = postprocessing_op(scores=training.outputs["scores"])

if __name__ == '__main__':
  import kfp.compiler as compiler
  compiler.Compiler().compile(kubeflow_training, "training-pipeline.yaml")
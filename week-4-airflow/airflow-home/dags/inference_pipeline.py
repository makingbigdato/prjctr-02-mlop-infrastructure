from datetime import datetime

from airflow import DAG
from airflow.models import Variable
from airflow.providers.cncf.kubernetes.operators.kubernetes_pod import KubernetesPodOperator
from kubernetes.client import models as k8s


volume = k8s.V1Volume(name="inference-storage", persistent_volume_claim=k8s.V1PersistentVolumeClaimVolumeSource(claim_name="inference-storage"),)
volume_mount = k8s.V1VolumeMount(name="inference-storage", mount_path="/tmp", sub_path=None)


DATASET_PATH = "/tmp/dataset.json"
MODEL_PATH = "/tmp/cls.pekl"
RESULT_PATH = "/tmp/results.json"

WANDB_PROJECT = Variable.get("WANDB_PROJECT")
WANDB_API_KEY = Variable.get("WANDB_API_KEY")

with DAG(
    description="Airflow Inference on K8S", 
    catchup=False, 
    dag_id="inference_dag",
    start_date=datetime(2021, 1, 1),
    schedule=None,
    tags=["K8S", "Course", "Inference"]) as dag:

    clean_storage_before_start = KubernetesPodOperator(
        name="clean_storage_before_start",
        image="bash:latest",
        cmds=["rm", "-rf", "/tmp/*"],  # actually it doesn't work as expected
        task_id="clean_storage_before_start",
        in_cluster=False,
        namespace="default",
        volumes=[volume],
        volume_mounts=[volume_mount],
    )

    load_dataset = KubernetesPodOperator(
        name="download_training_dataset",
        image="yevhenk10s/datadownloader:latest",
        cmds=[
            "python3", "/load-data/download-dataset.py", 
            "--n-samples", "200",
            "--noise", "0.3",
            "--random-state", "0",
            "--out-file", DATASET_PATH,
        ],
        task_id="download_training_dataset",
        in_cluster=False,
        namespace="default",
        volumes=[volume],
        volume_mounts=[volume_mount],
    )

    download_model = KubernetesPodOperator(
        name="download_model",
        image="yevhenk10s/artifacthandler:latest",
        cmds=[
            "python3", "/artifact-handler/handler.py", 
            "--save-to", "/tmp/",
        ],
        task_id="download_model",
        in_cluster=False,
        namespace="default",
        env_vars={
            "WANDB_PROJECT": WANDB_PROJECT,
            "WANDB_API_KEY": WANDB_API_KEY,
        },
        volumes=[volume],
        volume_mounts=[volume_mount],
    )

    inference = KubernetesPodOperator(
        name="inference",
        image="yevhenk10s/inference:latest",
        cmds=[
            "python3", "/inference-dir/inference-pipeline.py",
            "--model-path", MODEL_PATH,
            "--data-path", DATASET_PATH,
            "--results-path", RESULT_PATH,
        ],
        task_id="inference",
        in_cluster=False,
        namespace="default",
        volumes=[volume],
        volume_mounts=[volume_mount],
    )

    upload_results = KubernetesPodOperator(
        name="upload_results",
        image="yevhenk10s/artifacthandler:latest",
        cmds=[
            "python3", "/artifact-handler/handler.py", 
            "--model-path", RESULT_PATH,
        ],
        task_id="upload_results",
        in_cluster=False,
        namespace="default",
        env_vars={
            "WANDB_PROJECT": WANDB_PROJECT,
            "WANDB_API_KEY": WANDB_API_KEY,
        },
        volumes=[volume],
        volume_mounts=[volume_mount],
    )

    clean_up = KubernetesPodOperator(
        name="clean_up",
        image="bash:latest",
        cmds=["rm", "-rf", DATASET_PATH, RESULT_PATH, MODEL_PATH],
        task_id="clean_up",
        in_cluster=False,
        namespace="default",
        volumes=[volume],
        volume_mounts=[volume_mount],
        trigger_rule="all_done",
    )

clean_storage_before_start >> load_dataset >> download_model >> inference >> upload_results >> clean_up
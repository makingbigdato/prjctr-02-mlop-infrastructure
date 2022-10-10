from datetime import datetime

from airflow import DAG
from airflow.models import Variable
from airflow.providers.cncf.kubernetes.operators.kubernetes_pod import KubernetesPodOperator
from kubernetes.client import models as k8s


volume = k8s.V1Volume(name="training-storage", persistent_volume_claim=k8s.V1PersistentVolumeClaimVolumeSource(claim_name="training-storage"),)
volume_mount = k8s.V1VolumeMount(name="training-storage", mount_path="/tmp", sub_path=None)


# -------------
# TODO: Investigate https://airflow.apache.org/docs/apache-airflow-providers-cncf-kubernetes/2.0.3/_modules/airflow/providers/cncf/kubernetes/example_dags/example_kubernetes.html
# -------------

DATASET_PATH = "/tmp/dataset.json"
SCORES_PATH = "/tmp/scores.json"
MODEL_PATH = "/tmp/cls.pekl"

WANDB_PROJECT = Variable.get("WANDB_PROJECT")
WANDB_API_KEY = Variable.get("WANDB_API_KEY")

with DAG(
    description="Airflow Training on K8S", 
    catchup=False, 
    dag_id="training_dag",
    start_date=datetime(2021, 1, 1),
    schedule=None,
    tags=["K8S", "Course"]) as dag:

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

    train_model = KubernetesPodOperator(
        name="train_model",
        image="yevhenk10s/trainonkuber:latest",
        cmds=[
            "python3", "/train-dir/train-pipeline.py", 
            "--dataset-path", DATASET_PATH,
            "--scores-path", SCORES_PATH,
            "--out-model-path", MODEL_PATH,
            "--max-depth", "5",
            "--n-estimators", "10",
            "--max-features", "1",
            "--random-state", "1337",
        ],
        task_id="train_model",
        in_cluster=False,
        namespace="default",
        volumes=[volume],
        volume_mounts=[volume_mount],
    )

    upload_model = KubernetesPodOperator(
        name="upload_model",
        image="yevhenk10s/artifacthandler:latest",
        cmds=[
            "python3", "/artifact-handler/handler.py", 
            "--model-path", MODEL_PATH,
        ],
        task_id="upload_model",
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
        cmds=["rm", "-rf", DATASET_PATH, SCORES_PATH, MODEL_PATH],
        task_id="clean_up",
        in_cluster=False,
        namespace="default",
        volumes=[volume],
        volume_mounts=[volume_mount],
        trigger_rule="all_done",
    )


clean_storage_before_start >> load_dataset >> train_model >> upload_model >> clean_up
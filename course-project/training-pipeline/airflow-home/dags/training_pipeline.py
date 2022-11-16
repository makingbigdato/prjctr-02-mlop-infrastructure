from datetime import datetime

from airflow import DAG
from airflow.models import Variable
from airflow.providers.cncf.kubernetes.operators.kubernetes_pod import KubernetesPodOperator
from kubernetes.client import models as k8s



volume = k8s.V1Volume(name="training-storage", persistent_volume_claim=k8s.V1PersistentVolumeClaimVolumeSource(claim_name="training-storage"),)
volume_mount = k8s.V1VolumeMount(name="training-storage", mount_path="/tmp", sub_path=None)
# resources = k8s.V1ResourceRequirements(requests={"limit_gpu": "1"})

DATASET_PATH = "/tmp/dataset"
MODEL_PATH = "/tmp/model/"
EPOCHS = "1"

MINIO_USER = Variable.get("MINIO_USER")
MINIO_PASSWORD = Variable.get("MINIO_PASSWORD")


with DAG(
    description="Airflow Training on K8S", 
    catchup=False, 
    dag_id="training_dag",
    start_date=datetime(2021, 1, 1),
    schedule=None,
    tags=["K8S", "Course", "Final Project"]) as dag:

    clean_storage_before_start = KubernetesPodOperator(
        name="clean_storage_before_start",
        image="bash:latest",
        cmds=["rm", "-rf", "/tmp/*"],
        task_id="clean_storage_before_start",
        in_cluster=False,
        namespace="default",
        volumes=[volume],
        volume_mounts=[volume_mount],
    )

    load_dataset = KubernetesPodOperator(
        name="download_train_test_dataset",
        image="yevhenk10s/artefact-handler:latest",
        # mc alias set project http://192.168.1.104:9000 minio minio123
        # mc cp --recursive  project/dataset /tmp/ --> /tmp/dataset/{train|test}
        cmds=["/usr/local/bin/bash", "-xec"],
        arguments=[
            f"mc alias set project http://192.168.1.104:9000 {MINIO_USER} {MINIO_PASSWORD} && \
            pwd && \
            mc admin info project && \
            mc cp --recursive  project/dataset /tmp/ && \
            ls -lah {DATASET_PATH}"
        ],
        task_id="download_train_test_dataset",
        in_cluster=False,
        namespace="default",
        volumes=[volume],
        volume_mounts=[volume_mount],
    )

    test_dataset = KubernetesPodOperator(
        name="test_train_test_dataset",
        image="yevhenk10s/dataset-tester:latest",
        cmds=["python", "-m", "pytest", "-s"],
        arguments=[
            
            "test_dataset.py",
            "--dataset-path", DATASET_PATH,
        ],
        task_id="test_train_test_dataset",
        in_cluster=False,
        namespace="default",
        volumes=[volume],
        volume_mounts=[volume_mount],
    )

    test_code_and_model = KubernetesPodOperator(
        name="test_code_and_model",
        image="yevhenk10s/trainer:latest",
        cmds=["python", "-m", "pytest", "-s"],
        arguments=[
            "test_code.py",
            "test_model.py",
            "--dataset-path", DATASET_PATH,
            "--save-to", MODEL_PATH,
            "--epochs", EPOCHS,
        ],
        task_id="test_code_and_model",
        in_cluster=False,
        namespace="default",
        volumes=[volume],
        volume_mounts=[volume_mount],
    )

    train_model = KubernetesPodOperator(
        name="train_model",
        image="yevhenk10s/trainer:latest",
        # python main.py /tmp/dataset ./model 1
        cmds=[
            "python3", "/train/main.py", 
            DATASET_PATH,
            MODEL_PATH,
            EPOCHS,
        ],
        task_id="train_model",
        in_cluster=False,
        namespace="default",
        volumes=[volume],
        volume_mounts=[volume_mount],
        # container_resources=resources,
    )

    upload_model = KubernetesPodOperator(
        name="upload_model",
        image="yevhenk10s/artefact-handler:latest",
        # mc alias set project http://192.168.1.104:9000 minio minio123
        # mc cp --recursive project/model /tmp/model --> /tmp/dataset/{train|test}
        cmds=["/usr/local/bin/bash", "-xec"],
        arguments=[
            f"mc alias set project http://192.168.1.104:9000 {MINIO_USER} {MINIO_PASSWORD} && \
            pwd && \
            mc admin info project && \
            mc cp --recursive {MODEL_PATH} project/model && \
            mc ls project/model"
        ],
        task_id="upload_model",
        in_cluster=False,
        namespace="default",
        volumes=[volume],
        volume_mounts=[volume_mount],
    )

    clean_up = KubernetesPodOperator(
        name="clean_up",
        image="bash:latest",
        cmds=["rm", "-rf", DATASET_PATH, MODEL_PATH],
        task_id="clean_up",
        in_cluster=False,
        namespace="default",
        volumes=[volume],
        volume_mounts=[volume_mount],
        trigger_rule="all_done",
    )


# clean_storage_before_start >> load_dataset >> train_model >> upload_model >> clean_up
clean_storage_before_start >> load_dataset >> test_dataset >> train_model
load_dataset >> test_code_and_model >> train_model
train_model >> upload_model >> clean_up

import wandb
import argparse


PROJECT = "artifact-storage"
ENTITY = "yevhen-k-team"
run = wandb.init(project=PROJECT, entity=ENTITY)


def upload_model(model_path: str):
    artifact = wandb.Artifact('model', type='model')
    artifact.add_file(model_path)
    run.log_artifact(artifact)
    wandb.run.finish()


def download_model(model_path: str):
    artifact = run.use_artifact(f'{ENTITY}/{PROJECT}/model:latest', type='model')
    artifact_dir = artifact.download(root=model_path)
    print(artifact_dir)
    wandb.run.finish()


if __name__ == "__main__":
    # python --model-path=../train-model/cls.pekl
    # pythin --save-to=../train-model/
    parser = argparse.ArgumentParser(description='Save/Load Model')
    parser.add_argument('--model-path', type=str, required=False)
    parser.add_argument('--save-to', type=str, required=False)

    args = parser.parse_args()

    if args.model_path:
        upload_model(args.model_path)
    if args.save_to:
        download_model(args.save_to)

from minio import Minio
from minio.error import S3Error


def main():
    client = Minio(
        "localhost:8080",
        access_key="miniouser",
        secret_key="miniopassword",
        secure=False,
    )
    # Make 'dataset' bucket if not exist.
    found = client.bucket_exists("dataset")
    if not found:
        client.make_bucket("dataset")
    else:
        print("Bucket 'dataset' already exists")

    # Upload './file_uploader.py' as object name
    # 'file_uploader.py' to bucket 'dataset'.
    client.fput_object(
        "dataset", "file_uploader.py", "./file_uploader.py",
    )
    print(
        "'./file_uploader.py' is successfully uploaded as "
        "object 'file_uploader.py' to bucket 'dataset'."
    )


if __name__ == "__main__":
    try:
        main()
    except S3Error as exc:
        print("error occurred.", exc)

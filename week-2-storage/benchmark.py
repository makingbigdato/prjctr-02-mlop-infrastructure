"""
Insired by:
- https://github.com/devforfu/pandas-formats-benchmark
- https://oak-tree.tech/blog/pandas-minio-uploading-downloading-files
"""

from io import BytesIO
import os
import pandas as pd
import numpy as np
from timeit import default_timer
import time
from minio import Minio
from minio.deleteobjects import DeleteObject


ROOT_CSV_DIR = "./csv/"
BUCKET_NAME = "benchmarkbucket"
CLIENT = Minio(
            "localhost:8080",
            access_key="miniouser",
            secret_key="miniopassword",
            secure=False,
        )


def init():
    buckets = [bucket.name for bucket in CLIENT.list_buckets()]
    if not BUCKET_NAME in buckets:
        CLIENT.make_bucket(BUCKET_NAME)

    if not os.path.exists(ROOT_CSV_DIR):
        os.mkdir(ROOT_CSV_DIR)


def clean_dataframes():
    # local clean-up
    csvs = os.listdir(ROOT_CSV_DIR)
    for csv in csvs:
        if os.path.exists(ROOT_CSV_DIR + csv):
            os.remove(ROOT_CSV_DIR + csv)


def tear_down():
    # local clean-up
    csvs = os.listdir(ROOT_CSV_DIR)
    for csv in csvs:
        if os.path.exists(ROOT_CSV_DIR + csv):
            os.remove(ROOT_CSV_DIR + csv)
    
    # storage clean-up
    objects = CLIENT.list_objects(BUCKET_NAME)
    file_names = [o.object_name for o in objects]
    errors = CLIENT.remove_objects(
                BUCKET_NAME,
                [
                    DeleteObject(file) for file in file_names
                ],
            )
    for error in errors:
        print("error occured when deleting object", error)
    if BUCKET_NAME in CLIENT.list_buckets():
        CLIENT.remove_bucket(BUCKET_NAME)


def generate_dataset(n_rows, num_count, cat_count, max_nan=0.1, max_cat_size=100):
    """Randomly generate datasets with numerical and categorical features.
    
    The numerical features are taken from the normal distribution X ~ N(0, 1).
    The categorical features are generated as random uuid4 strings with 
    cardinality C where 2 <= C <= max_cat_size.
    
    Also, a max_nan proportion of both numerical and categorical features is replaces
    with NaN values.
    """
    dataset, types = {}, {}
    
    def generate_categories():
        from uuid import uuid4
        category_size = np.random.randint(2, max_cat_size)
        return [str(uuid4()) for _ in range(category_size)]
    
    for col in range(num_count):
        name = f'n{col}'
        values = np.random.normal(0, 1, n_rows)
        nan_cnt = np.random.randint(1, int(max_nan*n_rows))
        index = np.random.choice(n_rows, nan_cnt, replace=False)
        values[index] = np.nan
        dataset[name] = values
        types[name] = 'float32'
        
    for col in range(cat_count):
        name = f'c{col}'
        cats = generate_categories()
        values = np.array(np.random.choice(cats, n_rows, replace=True), dtype=object)
        nan_cnt = np.random.randint(1, int(max_nan*n_rows))
        index = np.random.choice(n_rows, nan_cnt, replace=False)
        values[index] = np.nan
        dataset[name] = values
        types[name] = 'object'
    
    return pd.DataFrame(dataset), types


def main():
    init()

    repeats = 5
    # For the next params the data set size is 96.2 MiB (100,865,761 bytes)
    csv_size_mb = 100_865_761 / 1024 / 1024
    n_rows = 125_000
    num_count = 15
    cat_count = 15
    dataset, _ = generate_dataset(n_rows=n_rows, num_count=num_count, cat_count=cat_count)

    # Saving with Pandas in CSV format
    start = default_timer()
    for i in range(repeats):
        dataset.to_csv(ROOT_CSV_DIR + f"dataset_{str(i).zfill(3)}", index=None)
    elapsed = default_timer() - start
    print(f"[Pandas/CSV] Total time for saving {repeats} datasets: {time.strftime('%H:%M:%S', time.gmtime(elapsed))}")
    print(f"[Pandas/CSV] Average time for saving dataset: {elapsed/repeats} sec")
    pd_total_write_time_csv = elapsed
    pd_mean_write_time_csv = elapsed / repeats
    pd_mean_write_speed_csv_mb_per_sec = (csv_size_mb * repeats) / elapsed

    # Reading with Pandas in CSV format
    start = default_timer()
    dfs = []
    for i in range(repeats):
        dfs.append(pd.read_csv(ROOT_CSV_DIR + f"dataset_{str(i).zfill(3)}"))
    elapsed = default_timer() - start
    print(f"[Pandas/CSV] Total time for reading {repeats} datasets: {time.strftime('%H:%M:%S', time.gmtime(elapsed))}")
    print(f"[Pandas/CSV] Average time for reading dataset: {elapsed/repeats} sec")
    pd_total_read_time_csv = elapsed
    pd_mean_read_time_csv = elapsed / repeats
    pd_mean_read_speed_csv_mb_per_sec = (csv_size_mb * repeats) / elapsed

    clean_dataframes()

    # Saving with Pandas in hdfs5 format
    start = default_timer()
    for i in range(repeats):
        dataset.to_hdf(ROOT_CSV_DIR + f"dataset_{str(i).zfill(3)}", mode="w", key="df")
    elapsed = default_timer() - start
    print(f"[Pandas/HDFS] Total time for saving {repeats} datasets: {time.strftime('%H:%M:%S', time.gmtime(elapsed))}")
    print(f"[Pandas/HDFS] Average time for saving dataset: {elapsed/repeats} sec")
    pd_total_write_time_hdfs = elapsed
    pd_mean_write_time_hdfs = elapsed / repeats
    pd_mean_write_speed_hdfs_mb_per_sec = (csv_size_mb * repeats) / elapsed

    # Reading with Pandas from hdfs5 format
    start = default_timer()
    dfs = []
    for i in range(repeats):
        dfs.append(pd.read_hdf(ROOT_CSV_DIR + f"dataset_{str(i).zfill(3)}"))
    elapsed = default_timer() - start
    print(f"[Pandas/HDFS] Total time for reading {repeats} datasets: {time.strftime('%H:%M:%S', time.gmtime(elapsed))}")
    print(f"[Pandas/HDFS] Average time for reading dataset: {elapsed/repeats} sec")
    pd_total_read_time_hdfs = elapsed
    pd_mean_read_time_hdfs = elapsed / repeats
    pd_mean_read_speed_hdfs_mb_per_sec = (csv_size_mb * repeats) / elapsed

    clean_dataframes()

    # Saving with Pandas in parquet format
    start = default_timer()
    for i in range(repeats):
        dataset.to_parquet(ROOT_CSV_DIR + f"dataset_{str(i).zfill(3)}", compression='gzip')
    elapsed = default_timer() - start
    print(f"[Pandas/PARQUET] Total time for saving {repeats} datasets: {time.strftime('%H:%M:%S', time.gmtime(elapsed))}")
    print(f"[Pandas/PARQUET] Average time for saving dataset: {elapsed/repeats} sec")
    pd_total_write_time_parquet = elapsed
    pd_mean_write_time_parquet = elapsed / repeats
    pd_mean_write_speed_parquet_mb_per_sec = (csv_size_mb * repeats) / elapsed

    # Reading with Pandas from parquet format
    start = default_timer()
    dfs = []
    for i in range(repeats):
        dfs.append(pd.read_parquet(ROOT_CSV_DIR + f"dataset_{str(i).zfill(3)}"))
    elapsed = default_timer() - start
    print(f"[Pandas/PARQUET] Total time for reading {repeats} datasets: {time.strftime('%H:%M:%S', time.gmtime(elapsed))}")
    print(f"[Pandas/PARQUET] Average time for reading dataset: {elapsed/repeats} sec")
    pd_total_read_time_parquet = elapsed
    pd_mean_read_time_parquet = elapsed / repeats
    pd_mean_read_speed_parquet_mb_per_sec = (csv_size_mb * repeats) / elapsed

    clean_dataframes()

    # Uploading datasets to the bucket
    start = default_timer()
    for i, df in enumerate(dfs):
        csv_bytes = df.to_csv().encode('utf-8')
        csv_buffer = BytesIO(csv_bytes)
        CLIENT.put_object(
            BUCKET_NAME, 
            "dataset_" + str(i).zfill(3),
            data=csv_buffer, 
            length=len(csv_bytes), 
            content_type='application/csv')
    elapsed = default_timer() - start
    print(f"[Pandas/Minio] Total time for uploading {repeats} datasets: {time.strftime('%H:%M:%S', time.gmtime(elapsed))}")
    print(f"[Pandas/Minio] Average time for uploading dataset: {elapsed/repeats} sec")
    minio_total_upload_time_csv = elapsed
    minio_mean_upload_time_csv = elapsed / repeats
    minio_mean_upload_speed_csv_mb_per_sec = (csv_size_mb * repeats) / elapsed
    
    # Download datasets from the bucket
    objects = CLIENT.list_objects(BUCKET_NAME)
    start = default_timer()
    for obj in objects:
        obj = CLIENT.get_object(
            BUCKET_NAME,
            obj.object_name
            )
        df = pd.read_csv(obj)
    elapsed = default_timer() - start
    print(f"[Pandas/Minio] Total time for downloading {repeats} datasets: {time.strftime('%H:%M:%S', time.gmtime(elapsed))}")
    print(f"[Pandas/Minio] Average time for downloading dataset: {elapsed/repeats} sec")
    minio_total_download_time_csv = elapsed
    minio_mean_download_time_csv = elapsed / repeats
    minio_mean_download_speed_csv_mb_per_sec = (csv_size_mb * repeats) / elapsed

    # Benchmark, speed of reading and writing, Mb/sec
    pandas = [pd_mean_write_speed_csv_mb_per_sec, pd_mean_read_speed_csv_mb_per_sec]
    minio = [minio_mean_upload_speed_csv_mb_per_sec, minio_mean_download_speed_csv_mb_per_sec]
    hdfs5 = [pd_mean_write_speed_hdfs_mb_per_sec, pd_mean_read_speed_hdfs_mb_per_sec]
    parquet = [pd_mean_write_speed_parquet_mb_per_sec, pd_mean_read_speed_parquet_mb_per_sec]
    index = ["write", "read"]
    df = pd.DataFrame({'pandas': pandas,
                    'minio': minio,
                    'hdfs5': hdfs5,
                    'parquet': parquet}, index=index)
    ax = df.plot.bar(rot=0, title="Data Processing Speed (Mb/sec)")
    fig = ax.get_figure()
    fig.savefig('benchmark-speed.png')

    # Benchmark, time for reading and writing of 1Mb
    pandas = [1/pd_mean_write_speed_csv_mb_per_sec, 1/pd_mean_read_speed_csv_mb_per_sec]
    minio = [1/minio_mean_upload_speed_csv_mb_per_sec, 1/minio_mean_download_speed_csv_mb_per_sec]
    hdfs5 = [1/pd_mean_write_speed_hdfs_mb_per_sec, 1/pd_mean_read_speed_hdfs_mb_per_sec]
    parquet = [1/pd_mean_write_speed_parquet_mb_per_sec, 1/pd_mean_read_speed_parquet_mb_per_sec]
    index = ["write", "read"]
    df = pd.DataFrame({'pandas': pandas,
                    'minio': minio,
                    'hdfs5': hdfs5,
                    'parquet': parquet}, index=index)
    ax = df.plot.bar(rot=0, title="Time for processing 1Mb")
    fig = ax.get_figure()
    fig.savefig('benchmark-time.png')

    tear_down()


if __name__ == "__main__":
    main()

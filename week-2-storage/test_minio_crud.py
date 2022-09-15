import unittest
from minio import Minio
from minio.deleteobjects import DeleteObject
import random
import string
import os
import hashlib

class TestMinioCRUD(unittest.TestCase):

    """
    Testing of some fucntionality provided by Minio SDK for Python.
    https://docs.min.io/docs/python-client-api-reference.html
    """

    def get_random_name(self):
        return ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(20))
    
    def create_files(self):
        for file in self.file_names:
            with open(file, 'wb') as fout:
                fout.write(os.urandom(1024))

    def create_filled_bucked(self):
        self.client.make_bucket(self.bucket_name)
        for file in self.file_names:
            self.client.fput_object(
                self.bucket_name, file, file,
            )

    def setUp(self):
        self.client = Minio(
            "localhost:8080",
            access_key="miniouser",
            secret_key="miniopassword",
            secure=False,
        )
        self.bucket_name = self.get_random_name()
        self.file_names = sorted([self.get_random_name() for _ in range(10)])
        self.create_files()

        self.md5sums = []
        for file in self.file_names:
            with open(file, "rb") as f:
                self.md5sums.append(
                    hashlib.md5(f.read()).hexdigest()
                )
        self.md5sums = sorted(self.md5sums)


    def tearDown(self):
        # delete all files locally 
        for file in self.file_names:
            if os.path.exists(file):
                os.remove(file)
        # delete all files on the storage
        if self.client.bucket_exists(self.bucket_name):
            errors = self.client.remove_objects(
                self.bucket_name,
                [
                    DeleteObject(file) for file in self.file_names
                ],
            )
            for error in errors:
                print("error occured when deleting object", error)
        if self.bucket_name in self.client.list_buckets():
            self.client.remove_bucket(self.bucket_name)

    # Bucket test

    def test_make_bucket(self):
        """Create bucket test"""
        self.client.make_bucket(self.bucket_name)
        self.assertTrue(self.client.bucket_exists(self.bucket_name))
    
    def test_list_buckets(self):
        """Read bucket test"""
        self.client.make_bucket(self.bucket_name)
        buckets = self.client.list_buckets()
        bucket_names = [bucket.name for bucket in buckets]
        self.assertIn(self.bucket_name, bucket_names)

    # There are no possible test to update bucket name

    def test_remove_bucket(self):
        """Delete bucket test"""
        self.client.make_bucket(self.bucket_name)
        self.client.remove_bucket(self.bucket_name)
        buckets = self.client.list_buckets()
        bucket_names = [bucket.name for bucket in buckets]
        self.assertNotIn(self.bucket_name,  bucket_names)
    
    # Bucket content tests

    def test_fput_object(self):
        """Upload file to the bucket"""
        # 1. put the files to the storage
        self.client.make_bucket(self.bucket_name)
        for file in self.file_names:
            self.client.fput_object(
                self.bucket_name, file, file,
            )
        # 2. get file names on the storage
        objects = self.client.list_objects(self.bucket_name)
        object_names = [obj.object_name for obj in objects]
        object_names = sorted(object_names)
        self.assertEqual(self.file_names, object_names)
    
    def test_fget_object(self):
        """Download file from the bucket"""
        # 0. initialize and fill the bucked
        self.create_filled_bucked()
        # 1. remove local files if any
        for file in self.file_names:
            if os.path.exists(file) and os.path.isfile(file):
                os.remove(file)
        # 2. download all files from the storage
        for file in self.file_names:
            _ = self.client.fget_object(self.bucket_name, object_name=file, file_path=file)
        
        # 3. get md5sums for downloaded files
        md5sums = []
        for file in self.file_names:
            with open(file, "rb") as f:
                md5sums.append(
                    hashlib.md5(f.read()).hexdigest()
                )
        md5sums = sorted(md5sums)
        self.assertEqual(self.md5sums, md5sums)

    def test_remove_object(self):
        """Remove file from the bucket"""
        # 0. initialize and fill the bucked
        self.create_filled_bucked()
        # 1. chose a file to delete 
        file = random.choice(self.file_names)
        # 2. remove file from lists, locally, and remotely
        self.file_names.remove(file)
        os.remove(file)
        self.client.remove_object(self.bucket_name, file)
        # 3. get file names on the storage and compare them with local files
        objects = self.client.list_objects(self.bucket_name)
        object_names = [obj.object_name for obj in objects]
        object_names = sorted(object_names)
        self.file_names = sorted(self.file_names)
        self.assertEqual(self.file_names, object_names)
        

if __name__ == "__main__":
    unittest.main()

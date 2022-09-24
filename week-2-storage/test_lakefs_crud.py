import pandas as pd
from pprint import pprint
import lakefs_client
from lakefs_client import models
from lakefs_client.client import LakeFSClient

# Docs are aveilable at:
# - https://docs.lakefs.io/integrations/python.html
# - https://pydocs.lakefs.io/

# lakeFS credentials and endpoint
configuration = lakefs_client.Configuration()
configuration.username = 'AKIAJ6D2EKUTNRCWJYTQ'
configuration.password = '4k7o+H3nVvaArr4oVI++oZ0W6ZU6vxBiarFtGAyh'
configuration.host = 'http://localhost:8000'

client = LakeFSClient(configuration)


def create_branch():
    res = client.branches.create_branch(
        repository="lakefs-datasets",
        branch_creation=models.BranchCreation(
        name="dev", 
        source="master"))
    pprint(f"create_branch(): {res}")


def read_branch():
    res = client.branches.get_branch(repository="lakefs-datasets", branch="dev")
    pprint(f"read_branch(): {res}")
    res = client.objects.list_objects(repository="lakefs-datasets", ref="dev")
    pprint(f"read_branch(): {res}")


# def update_branch():...


def delete_branch():
    res = client.branches.delete_branch(
        repository="lakefs-datasets",
        branch="dev")
    pprint(f"delete_branch(): {res}")


def create_file():
    with open('project-1-at-2022-09-18-11-29-88db0606.csv', 'rb') as f:
        res = client.objects.upload_object(
            repository="lakefs-datasets", 
            branch="dev", path='project-1-at-2022-09-18-11-29-88db0606.csv', content=f)
    pprint(f"create_file(): {res}")
    res = client.commits.commit(
        repository="lakefs-datasets",
        branch="dev",
        commit_creation=models.CommitCreation(message='Added a CSV file!', metadata={'using': 'python_api'}))
    pprint(f"create_file(): {res}")


def read_file():
    res = client.objects.get_object(repository="lakefs-datasets", ref="dev", path='project-1-at-2022-09-18-11-29-88db0606.csv')
    pprint(f"read_file(): {res}")
    with open("tmp.csv", "wb") as f:
        f.write(res.read())


def update_file():
    df = pd.read_csv("project-1-at-2022-09-18-11-29-88db0606.csv")
    # make dummy modification to the dataframe
    tmprow0, tmprow1 = df.iloc[0].copy(), df.iloc[1].copy()
    df.iloc[0], df.iloc[1] = tmprow1, tmprow0
    df.to_csv("project-1-at-2022-09-18-11-29-88db0606.csv", index=None)
    # upload file
    with open('project-1-at-2022-09-18-11-29-88db0606.csv', 'rb') as f:
        res = client.objects.upload_object(
            repository="lakefs-datasets", 
            branch="dev", path='project-1-at-2022-09-18-11-29-88db0606.csv', content=f)
    # commit changes
    res = client.commits.commit(
        repository="lakefs-datasets",
        branch="dev",
        commit_creation=models.CommitCreation(message='New content', metadata={'using': 'python_api'}))
    pprint(f"create_file(): {res}")


def delete_file():
    res = client.objects.delete_object(repository="lakefs-datasets", branch="dev", path='project-1-at-2022-09-18-11-29-88db0606.csv')
    pprint(f"delete_file(): {res}")


def main():
    create_branch()
    read_branch()
    create_file()
    read_file()
    update_file()
    delete_file()
    delete_branch()


if __name__ == "__main__":
    main()

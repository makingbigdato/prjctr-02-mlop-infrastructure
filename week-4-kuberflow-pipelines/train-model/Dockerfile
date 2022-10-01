FROM python:3.10
WORKDIR /train-dir
COPY requirements.txt /train-dir
RUN pip install -r requirements.txt
COPY train-pipeline.py /train-dir

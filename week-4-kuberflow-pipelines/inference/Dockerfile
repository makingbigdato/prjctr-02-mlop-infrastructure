FROM python:3.10
WORKDIR /inference-dir
COPY requirements.txt /inference-dir
RUN pip install -r requirements.txt
COPY inference-pipeline.py /inference-dir

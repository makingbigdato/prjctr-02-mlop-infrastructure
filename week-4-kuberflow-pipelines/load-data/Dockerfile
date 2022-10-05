FROM python:3.10
WORKDIR /load-data
COPY requirements.txt /load-data
RUN pip install -r requirements.txt
COPY download-dataset.py /load-data
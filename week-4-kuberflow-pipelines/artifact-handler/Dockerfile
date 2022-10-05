FROM python:3.10
WORKDIR /artifact-handler
COPY requirements.txt /artifact-handler
RUN pip install -r requirements.txt
COPY handler.py /artifact-handler
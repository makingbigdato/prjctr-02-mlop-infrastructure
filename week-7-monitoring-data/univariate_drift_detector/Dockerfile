FROM python:3.10
WORKDIR /detector-dir
COPY requirements.txt /detector-dir
RUN pip install -r requirements.txt
COPY univariate_drift_detector.py /detector-dir

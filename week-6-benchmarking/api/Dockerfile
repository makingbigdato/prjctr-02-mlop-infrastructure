FROM nvidia/cuda:11.7.0-runtime-ubuntu20.04
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
RUN apt-get update -y && apt-get upgrade -y && apt-get install python3 python3-pip -y
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip3 install --upgrade pip && pip3 install -r requirements.txt
COPY . .
RUN gdown --fuzzy https://drive.google.com/file/d/1M5SFB5cYS7Q3oLpkEQVGERXtquwPxury/view\?usp\=sharing
RUN mv bert-base-uncased-regression-weights.pth ./weights/
CMD ["python3", "app.py"]
EXPOSE 5000
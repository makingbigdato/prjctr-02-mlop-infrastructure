FROM python:3.10-alpine3.16
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
# RUN apt-get update -y && apt-get upgrade -y
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip3 install --upgrade pip && pip3 install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["python3", "app.py"]
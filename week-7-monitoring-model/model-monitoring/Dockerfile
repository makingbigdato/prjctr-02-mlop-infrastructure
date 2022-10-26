FROM python:3.10
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /serving
RUN apt-get update -y && apt-get upgrade -y && apt-get install python3 python3-pip -y
COPY requirements.txt /serving

# RUN addgroup user && adduser --ingroup user --home /home/user --disabled-password user
# USER user
# ENV PATH="${PATH}:/home/user/.local/bin/"

# ENV PATH="${PATH}:/root/.local/bin"
RUN pip3 install --upgrade pip && pip3 install -r requirements.txt
# RUN pip3 install --user wandb==0.13.3

COPY Predictor.py /serving

# Port for GRPC
EXPOSE 5000
# Port for REST
EXPOSE 9000

# Define environment variables
ENV MODEL_NAME Predictor
ENV SERVICE_TYPE MODEL
ENV PERSISTENCE 0

# Fix possible issues with wandb and permissions
RUN chown -R 8888 /serving
RUN mkdir /.cache
RUN chmod 777 /.cache
RUN mkdir /.config
RUN chmod 777 /.config

CMD exec seldon-core-microservice $MODEL_NAME --service-type $SERVICE_TYPE --persistence $PERSISTENCE
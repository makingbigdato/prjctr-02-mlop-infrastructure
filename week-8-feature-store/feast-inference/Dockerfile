FROM python:3.10

WORKDIR /inference

RUN mkdir /train
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . . 

CMD [ "bash" ]
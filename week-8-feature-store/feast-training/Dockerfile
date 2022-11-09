FROM python:3.10

WORKDIR /train

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . . 

CMD [ "bash" ]
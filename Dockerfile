FROM python:3.9-slim-buster

WORKDIR /usr/src/app

RUN apt-get update && apt-get install gcc -y

RUN pip install --upgrade pip setuptools wheel

COPY ./requirements.txt /usr/src/app/requirements.txt
RUN pip install -r requirements.txt

COPY . /usr/src/app/

CMD python -u -m src
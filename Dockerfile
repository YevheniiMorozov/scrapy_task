FROM python:3.10

WORKDIR /apartments

COPY apartments/requirements.txt /apartments/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /apartments/requirements.txt

COPY ./apartments /apartments

WORKDIR /apartments

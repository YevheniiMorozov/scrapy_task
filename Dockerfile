FROM python:3.8

WORKDIR /usr/src/api

COPY requirements.txt ./

RUN pip install -r requirements.txt \
    && rm -rf /root/.cache/pip

COPY . .

WORKDIR /usr/src/api/apartments/apartments

RUN ls

EXPOSE 8000
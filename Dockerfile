# syntax=docker/dockerfile:1

FROM python:3.9.10-slim-bullseye 
WORKDIR /usr/src/app

ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# system dependencies
RUN apt-get update
RUN apt install -y git gcc python3-dev

# python dependencies
COPY ./requirements.txt .
COPY . .
RUN pip install --upgrade pip setuptools wheel
RUN pip install -r requirements.txt

CMD ["python", "-u", "main.py"]
FROM python:3.7-slim as base

MAINTAINER hjrendell@gmail.com

RUN echo "deb http://ftp.debian.org/debian sid main" >> /etc/apt/sources.list
RUN apt-get update && \
    apt-get install -y \
    libatlas-base-dev \
    libfreetype6-dev \
    libc6 \
    && rm -rf /var/lib/apt/lists/*
RUN pip install pipenv

WORKDIR /app

COPY Pipfile Pipfile.lock /app/
RUN pipenv lock -r > requirements.txt && \
    pip install --target /app/dist/ -r requirements.txt

ENV PYTHONPATH=/app/dist:$PYTHONPATH

COPY . /app

WORKDIR /app

CMD python -m karma.bot -t $DISCORD_TOKEN -d $KARMA_DB_PATH

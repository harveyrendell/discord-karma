FROM python:3.7-slim

MAINTAINER hjrendell@gmail.com

RUN apt-get update && \
    apt-get install -y \
    software-properties-common \
    libfreetype6-dev \
    build-essential \
    git

COPY . /app
WORKDIR /app

RUN pip install pipenv && \
    pipenv install --system --deploy

CMD python -m karma.bot -t $DISCORD_TOKEN -d $KARMA_DB_PATH
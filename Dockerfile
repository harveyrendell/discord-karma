from python:3.6-slim

MAINTAINER hjrendell@gmail.com

RUN apt-get update && apt-get install -y git

COPY . /app
WORKDIR /app

RUN pip install pipenv

RUN pipenv install --system --deploy

CMD python -m karma.bot -t $DISCORD_TOKEN -d $KARMA_DB_PATH

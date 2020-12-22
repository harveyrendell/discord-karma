FROM python:3.7-slim

MAINTAINER hjrendell@gmail.com

RUN echo "deb http://ftp.debian.org/debian sid main" >> /etc/apt/sources.list
RUN apt-get update && \
    apt-get install -y \
    libatlas-base-dev \
    libfreetype6-dev \
    libc6 \
    gcc
RUN pip install pipenv

WORKDIR /app

# Copy Pipfile separately to avoid running install every build
COPY Pipfile Pipfile.lock /app/

# Install from new index which serves wheels for ARM
RUN if [ $(uname -m) = armv7l ]; then \
        pipenv lock \
    ; fi

RUN pipenv install --system --deploy

COPY . /app

CMD python -m karma.bot -t $DISCORD_TOKEN -d $KARMA_DB_PATH

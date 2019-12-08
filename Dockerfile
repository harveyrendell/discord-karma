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

# Install from wheel on arm processors to avoid building from source
RUN if [ $(uname -m) = armv7l ]; then \
        pip install \
        https://www.piwheels.org/simple/kiwisolver/kiwisolver-1.1.0-cp37-cp37m-linux_armv7l.whl#sha256=a2cca06a73500969a33771eae6387e3d0c4163ee83d3078929e75cd893d1c179 \
        https://www.piwheels.org/simple/matplotlib/matplotlib-3.1.0-cp37-cp37m-linux_armv7l.whl#sha256=0c9119af96963801ff5e35362e5ca645249a1489fabbe1acc36b03ff1abdf500 \
        https://www.piwheels.org/simple/numpy/numpy-1.17.4-cp37-cp37m-linux_armv7l.whl#sha256=eda8f3c1ef64c797971a61012ec218cebe6c6f33e957b1baafbb34b933037098 \
    ; fi

WORKDIR /app

# Copy Pipfile separately to avoid running install every build
COPY Pipfile Pipfile.lock /app/
RUN pipenv install --system --deploy

COPY . /app

CMD python -m karma.bot -t $DISCORD_TOKEN -d $KARMA_DB_PATH

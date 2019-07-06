FROM python:3.7-slim

MAINTAINER hjrendell@gmail.com

RUN apt-get update && \
    apt-get install -y \
    libatlas-base-dev

RUN if [ $(uname -m) = armv7l ]; then \
        pip install \
        https://www.piwheels.org/simple/kiwisolver/kiwisolver-1.1.0-cp37-cp37m-linux_armv7l.whl#sha256=0d4b2d089fb73faaac0dcc8ff5237a0aee075d65f1adbe94a0483772c9db1a3a \
        https://www.piwheels.org/simple/matplotlib/matplotlib-3.1.0-cp37-cp37m-linux_armv7l.whl#sha256=46dcade5008d4a865afd2f781e44cfbac058c350c14ea474f5ea041ad752befd \
    ; fi


COPY . /app
WORKDIR /app

RUN pip install pipenv && \
    pipenv install --system --deploy

CMD python -m karma.bot -t $DISCORD_TOKEN -d $KARMA_DB_PATH
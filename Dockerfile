FROM python:3 AS build
ADD . /code
WORKDIR /code
RUN python setup.py sdist && \
    cp dist/$(python setup.py --fullname).tar.gz dist/discord-karma.tar.gz

FROM python:3.6-slim
COPY --from=build /code/dist/discord-karma.tar.gz /run
RUN pip install /run/discord-karma.tar.gz

ENTRYPOINT python -m karma.bot --token $DISCORD_TOKEN --db-path $KARMA_DB_PATH

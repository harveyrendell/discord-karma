## Karma Bot for Discord

## Install

This project uses [pipenv](https://pipenv.readthedocs.io/en/latest/) and requires Python 3.6. Karma Bot is installed in the following way:

```bash
pip install pipenv  # if you don't have it already
pipenv install
```

## Bot Setup
This bot uses the privileged server member intent to attach usernames to ids.
This can be set up in the Discord Developer Portal from Applications > Bot > Privileged Gateway Intents > Server Members Intent
![intent setting image](https://i.imgur.com/Rqk29gc.png)

## Use

```bash
pipenv run python -m karma.bot -t <discord-bot-token>
```

## Test

```bash
pipenv run pytest
```

## Build the docker container

1. You can build the docker container and push to a registry if you'd like
1. Run the following:
```bash
docker build -t <registry>/discord-karma:1.0.0
docker push <registry>/discord-karma:1.0.0
```

## Run on Kubernetes

1. Open the [deployment.yaml](./deployment.yaml) and add your TOKEN at the specific line and
change the location of the `image:` to a publicly accessable version built.
1. Run the following to run it on Kubernetes
```bash
kubectl apply -f deployment.yaml
```

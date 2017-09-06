# Nefario API

This repository contains the code for the API.

## Installation

Work so far only on a linux distribution. MacOS has some issues getting access to network port via docker.

### Virtualenv

Create a virtualenv and boostrap dependencies

    virtualenv -p python3 ~/venv/nefario-api
    pip install -r requirements.tests.txt

### Bootstrap infrastructure

For developpment purpose, use docker-compose to bootstrap a cluster made of :
- a salt master configure with API
- a salt minion
- an nginx server that forward request to
- the nefario API

    docker-compose up --build -d

### Tests

You should now be able to run the test suits using pytest in our venv

    pytest

# TEQBot

Mumble music bot with youtube, spotify integrations

<a href="https://github.com/psf/black"><img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>

## Installment

Copy `.env.example` file to `.env` and provide the necessary credentials from Spotify API.

Build the docker images with `docker-compose build` and run the project with `docker-compose up -d`

Run `pre-commit install` once to install pre-commit hooks before any development.

Deploy on production environment with `bash bin/deploy.sh`

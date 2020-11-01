#!/bin/bash

docker-compose -f production.yml build $2
docker-compose -f production.yml up -d $2

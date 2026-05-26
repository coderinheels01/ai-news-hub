#!/bin/bash
# Script to run Docker Compose with the correct env file
docker-compose -f docker/docker-compose.yml --env-file .env up "$@"
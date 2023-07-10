#!/bin/bash

# Postgres
docker run --name postgres \
  -e POSTGRES_USER="admin" \
  -e POSTGRES_PASSWORD="admin" \
  -e POSTGRES_DB="news_db" \
  -p 5433:5432 \
  -v postgres_data:/var/lib/postgresql/data \
  -v $(pwd)/init.sql:/docker-entrypoint-initdb.d/init.sql \
  postgres:latest

# docker run -d --name postgres \
#   -e POSTGRES_USER=${POSTGRES_USER} \
#   -e POSTGRES_PASSWORD=${POSTGRES_PASSWORD} \
#   -e POSTGRES_DB=${POSTGRES_DB} \
#   -v postgres_data:/var/lib/postgresql/data \
#   -v $(pwd)/init.sql:/docker-entrypoint-initdb.d/init.sql \
#   postgres:latest

# # NATS
# docker run --name nats -p 4222:4222 nats:latest
# docker run -d --name nats -p 4222:4222 nats:latest

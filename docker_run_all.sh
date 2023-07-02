#!/bin/bash

# Postgres
docker run --name postgres \
  -e POSTGRES_USER=admin \
  -e POSTGRES_PASSWORD=admin \
  -e POSTGRES_DB=news_db \
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

# # Build and run benzinga_newsfeed_websockets
# docker build -t benzinga_newsfeed_websockets ./benzinga_newsfeed_websockets
# docker run -d --name benzinga_newsfeed_websockets \
#   --env-file .env \
#   --link nats:nats \
#   --link postgres:postgres \
#   -v $(pwd)/benzinga_newsfeed_websockets:/app \
#   benzinga_newsfeed_websockets

# # Build and run db_writer
# docker build -t db_writer ./db_writer
# docker run -d --name db_writer \
#   --env-file .env \
#   --link nats:nats \
#   --link postgres:postgres \
#   -v $(pwd)/db_writer:/app \
#   db_writer

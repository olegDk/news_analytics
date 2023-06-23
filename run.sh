#!/bin/bash

source remove.sh
cd benzinga_newsfeed_websockets
protoc --python_out=. news.proto
cd ..
cp benzinga_newsfeed_websockets/news_pb2.py analytics/news_pb2.py
docker-compose up --build

#!/bin/bash

source remove.sh
cd benzinga_newsfeed_websockets
protoc --python_out=. news.proto
cd ..
cp benzinga_newsfeed_websockets/news_pb2.py db_writer/news_pb2.py
cp benzinga_newsfeed_websockets/news_pb2.py summary_service/news_pb2.py
docker-compose up --build

#!/bin/bash

# Get the container ID of the running postgres service
CONTAINER_ID=$(docker ps -qf "name=postgres")

# If no container was found, exit with an error message
if [ -z "$CONTAINER_ID" ]; then
    echo "No running postgres container found."
    exit 1
fi

# Start an interactive bash session on the postgres container
docker exec -it $CONTAINER_ID bash

# psql -U admin -l # to list all databases
# psql -U admin -d news_db # to enter news_db

# \dt                 # to list all tables
# SELECT * FROM news; # to query the news table
#!/bin/bash

docker network create aidsight

docker build docker-db -t aidsight-db
docker run --name aidsight-db --network aidsight --network-alias mongodb --detach aidsight-db
docker exec aidsight-db /load_backup.sh

tar -cf docker-app/app.tar app
docker build docker-app -t aidsight-app
docker run --name aidsight-app --network aidsight -p 80:80 --detach aidsight-app
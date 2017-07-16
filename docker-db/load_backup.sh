#!/bin/bash

load_backup() {
    echo 'Starting mongorestore...'
	mongorestore --db iati --collection $1 --drop dump/iati/$1.bson
}

cd /home/mongodb

echo 'Downloading from S3...'

if [ -f "$HOME/.aws/credentials" ]; then
	aws s3 cp s3://${S3_BUCKET}/mongodb_iati.tar.gz .
else
	wget https://s3-${S3_REGION}.amazonaws.com/${S3_BUCKET}/mongodb_iati.tar.gz
fi

echo 'Extracting archive...'
tar -zxf mongodb_iati.tar.gz

for collection in activities activities_metadata transactions organizations organizations_metadata quality cleaned_orgs_full scores; do
	load_backup ${collection}
done

echo 'Cleaning up...'
rm -rf dump
rm -f mongodb_iati.tar.gz
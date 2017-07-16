#!/bin/bash

add_backup() {
    echo 'Starting mongodump...'
    mongodump --db iati --collection $1
}

cd /home/mongodb

for collection in activities activities_metadata transactions organizations organizations_metadata quality cleaned_orgs_full scores; do
	add_backup ${collection}
done

echo 'Creating archive...'
tar -cf mongodb_iati.tar dump/iati
gzip mongodb_iati.tar

echo 'Uploading to S3...'
aws s3 cp mongodb_iati.tar.gz s3://${S3_BUCKET}/ --acl public-read

echo 'Cleaning up...'
rm -rf dump
rm -f mongodb_iati.tar.gz
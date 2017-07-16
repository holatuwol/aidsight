#!/bin/bash

source /etc/apache2/envvars
rm -f /var/run/apache2/apache2/apache2*.pid

if [ "" == "${FLASK_DEBUG}" ]; then
	apachectl -DFOREGROUND
else
    export LC_ALL=C.UTF-8
    export LANG=C.UTF-8

    cd /var/www/aidsight/app

	export FLASK_APP=aidsight.py

	flask run --host=0.0.0.0
fi
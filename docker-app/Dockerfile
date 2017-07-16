FROM ubuntu

RUN apt-get update && \
	apt-get install -y apache2 apache2-dev build-essential && \
	apt-get install -y git python3-dev python3-pip && \
	cd /usr/local/bin && ln -s /usr/bin/python3 python && cd -

RUN pip3 install --upgrade pip && \
	pip3 install boto numpy pandas pymongo flask flask_wtf requests ujson && \
	apt-get install -y libapache2-mod-wsgi-py3 && \
	mkdir -p /var/www/aidsight

ADD app.tar /var/www/aidsight/
ADD aidsight.conf /etc/apache2/sites-available/
ADD run.sh /

RUN chmod a+x *.sh && \
	chown -R www-data:www-data /var/www/aidsight && \
	a2dissite 000-default.conf && \
	a2ensite aidsight.conf && \
	cd -

EXPOSE 80
EXPOSE 5000

ENTRYPOINT [ "/run.sh" ]
FROM mongo:3.4

RUN	apt-get update && \
	apt-get install -y awscli vim wget

ADD load_backup.sh /
ADD store_backup.sh /

RUN mkdir -p /home/mongodb && \
	chown -R mongodb:mongodb /home/mongodb && \
	chown mongodb:mongodb /*.sh && \
	chmod a+x /*.sh

ENV S3_REGION us-west-2
ENV S3_BUCKET mdang.w210

USER mongodb
from continuumio/miniconda3

# Speed up JSON parsing

RUN	apt-get update && \
	apt-get install -y awscli git parallel vim && \
	apt-get install -y build-essential && \
	conda install --yes ujson

# Install basic Python libraries

RUN	apt-get -y install libblas-dev liblapack-dev libatlas-base-dev gfortran && \
	apt-get -y install libfreetype6-dev libpng12-dev pkg-config python-qt4

RUN conda install --yes chardet jupyter matplotlib networkx nltk pandas pymongo requests scikit-learn seaborn && \
	pip install geocoder xmltodict

# Prepare jupyter folders

RUN	useradd -ms /bin/bash jupyter && \
	mkdir -p /home/jupyter/notebook && \
	mkdir -p /home/jupyter/.jupyter && \
	echo "c.NotebookApp.token = u''" > /home/jupyter/.jupyter/jupyter_notebook_config.py && \
	echo "#!/bin/bash\njupyter notebook --ip=0.0.0.0 --no-browser --notebook-dir=/home/jupyter/notebook" > /entrypoint.sh && \
	chmod a+x /entrypoint.sh

ADD *.py /home/jupyter/notebook/
ADD *.ipynb /home/jupyter/notebook/

RUN	chown -R jupyter:jupyter /home/jupyter

EXPOSE 8888

USER jupyter

ENTRYPOINT ["/entrypoint.sh"]
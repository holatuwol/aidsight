**Note**: The process of generating the activity graph is implemented very simply by creating the graph entirely in memory. As a result, you will need to use a machine with a lot of available memory (equivalent to an ``r3.2xlarge`` or ``r4.2xlarge`` EC2 instance) in order to process the data set.

Start Docker Container
----------------------

Build a Docker image named ``aidsight-eda``.

.. code-block:: bash

	docker build -t aidsight-eda .

Create the container for performing the exploratory data analysis.

.. code-block:: bash

	docker run --name aidsight-eda --network aidsight --network-alias jupyter --detach aidsight-eda

Run ``aws configure`` in order to setup your credentials for uploading and downloading from S3.

.. code-block:: bash

	docker exec -it aidsight-eda aws configure

To navigate to Jupyter in your web browser, find the IP address for the container, and you can connect to Jupyter on port 8888.

.. code-block:: bash

	docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' aidsight-eda

Download XML Files
------------------

* `01-download-iati-activities.ipynb <01-download-iati-activities.ipynb>`__
* `02-download-iati-organisations.ipynb <02-download-iati-organisations.ipynb>`__

Load into MongoDB
-----------------

* `03-load-data-to-mongo-final.ipynb <03-load-data-to-mongo-final.ipynb>`__

Generate Relationship Graph
---------------------------

* `04-load-data-to-picklegraph.ipynb <04-load-data-to-picklegraph.ipynb>`__
* `05-check-graph-data.ipynb <05-check-graph-data.ipynb>`__
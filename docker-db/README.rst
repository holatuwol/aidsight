Start Docker Container
----------------------

Build a Docker image named ``aidsight-db``.

.. code-block:: bash

	docker build -t aidsight-db .

Create a network so that Aidsight-related containers can join.

.. code-block:: bash

	docker network create aidsight

Start up a container.

.. code-block:: bash

	docker run --name aidsight-db --network aidsight --network-alias mongodb --detach aidsight-db

Load Existing Backup
--------------------

If you're loading from an existing backup, you can use the following command:

.. code-block:: bash

	docker exec -e S3_BUCKET=your.s3.bucket aidsight-db /load_backup.sh

Store New Backup
----------------

If you're ready to store a backup (for example, you started from scratch and ran the notebooks for exploratory data analysis), you can use the following command:

.. code-block:: bash

	docker exec -e S3_BUCKET=your.s3.bucket aidsight-db /store_backup.sh
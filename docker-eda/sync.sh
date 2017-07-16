#!/bin/bash

for file in *.py; do
	docker cp aidsight-eda:/home/jupyter/notebook/$file .
done

for file in *.ipynb; do
	docker cp aidsight-eda:/home/jupyter/notebook/$file .
done

python cleanup_notebooks.py
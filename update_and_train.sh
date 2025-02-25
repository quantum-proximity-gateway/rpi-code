#!/bin/bash

cd #RPI CODE REPO DIRECTORY

git fetch origin main

if ! git diff --quiet HEAD origin/main; then
	echo "New updates found. Pulling changes..."

	git pull origin main

	echo "Running train_model.py..."
	python3 main/train_model.py
else
	echo "No updates found."
fi

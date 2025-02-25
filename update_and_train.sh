#!/bin/bash

cd #/path/to/repo/

git fetch origin main

if ! git diff --quiet HEAD origin/main; then
	echo "New updates found. Pulling changes..."

	git pull origin main

	echo "Running train_model.py..."
	python3 main/train_model.py
else
	echo "No updates found."
fi

# To schedule this script to run automatically, add a new cron job by running `crontab -e`, and paste the following at the end:
#
# ```
# */1 * * * * /path/to/repo/update_and_train.sh >> /path/to/repo/update.log 2>&1
# ```
#
# This will:
# - run the script every 1 minute
# - log output to update.log for debugging

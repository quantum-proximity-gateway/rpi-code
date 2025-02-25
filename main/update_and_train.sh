#!/usr/bin/env bash

set -e

if [ -f .env ]; then
  source .env
fi

if [ -z "$GITHUB_AUTH_PULL_TOKEN" ]; then
  echo "Error: GITHUB_TOKEN not set. Make sure it's defined in .env or in your environment."
  exit 1
fi

GITHUB_USERNAME="quantum-proximity-gateway"
REPO_NAME="rpi-code"
BRANCH="main"

GIT_REMOTE_URL="https://${GITHUB_AUTH_PULL_TOKEN}@github.com/${GITHUB_USERNAME}/${REPO_NAME}.git"

cd ../

git remote set-url origin "$GIT_REMOTE_URL"

git fetch origin

LOCAL_COMMIT=$(git rev-parse HEAD)
REMOTE_COMMIT=$(git rev-parse origin/"${BRANCH}")

if [ "$LOCAL_COMMIT" != "$REMOTE_COMMIT" ]; then
  echo "Pulling latest changes from $BRANCH..."
  git pull origin "$BRANCH"
else
  echo "Local repository is up-to-date with origin/$BRANCH."
fi

face_rec/bin/python main/train_model.py
echo "Running train_model.py..."
g
# To schedule this script to run automatically, add a new cron job by running `crontab -e`, and paste the following at the end:
#
# ```
# */1 * * * * /path/to/repo/update_and_train.sh >> /path/to/repo/update.log 2>&1
# ```
#
# This will:
# - run the script every 1 minute
# - log output to update.log for debugging

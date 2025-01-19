#!/bin/bash

# Define the source and destination paths
SOURCE="./qpg_usb"
DESTINATION="/usr/bin/qpg_usb"

# Check if the source file exists
if [ ! -f "$SOURCE" ]; then
  echo "Error: File '$SOURCE' not found in the current directory."
  exit 1
fi

# Copy the file to the destination
sudo cp "$SOURCE" "$DESTINATION"

# Set the appropriate permissions to make it executable
sudo chmod +x "$DESTINATION"

# Verify the operation
if [ -f "$DESTINATION" ]; then
  echo "Successfully copied '$SOURCE' to '$DESTINATION' and made it executable."
else
  echo "Error: Failed to copy '$SOURCE' to '$DESTINATION'."
  exit 1
fi

# Add the @reboot cron job
CRON_JOB="@reboot sh $DESTINATION"

# Check if the cron job already exists
(crontab -l 2>/dev/null | grep -F "$CRON_JOB") && echo "Cron job already exists." && exit 0

# Add the cron job
(crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -

# Confirm the cron job has been added
if crontab -l | grep -Fq "$CRON_JOB"; then
  echo "Cron job added successfully: $CRON_JOB"
else
  echo "Error: Failed to add cron job."
  exit 1
fi

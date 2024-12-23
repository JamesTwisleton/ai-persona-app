#!/bin/bash

IMAGE_NAME="flask-app"

# Check if the --rebuild flag is passed
FORCE_REBUILD=false
if [[ "$1" == "--rebuild" ]]; then
  FORCE_REBUILD=true
fi

# Build or use existing image
if $FORCE_REBUILD; then
  echo "Force rebuild option selected. Building the image..."
  docker build -t "$IMAGE_NAME" .
elif docker image inspect "$IMAGE_NAME" > /dev/null 2>&1; then
  echo "Image $IMAGE_NAME already exists. Running it..."
else
  echo "Image $IMAGE_NAME not found. Building it..."
  docker build -t "$IMAGE_NAME" .
fi

# Run the Docker container
docker run -p 8050:8050 "$IMAGE_NAME"

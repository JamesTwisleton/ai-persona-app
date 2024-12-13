#!/bin/bash

IMAGE_NAME="persona-compass-app"

# Check if the image exists
if docker image inspect "$IMAGE_NAME" > /dev/null 2>&1; then
  echo "Image $IMAGE_NAME already exists. Running it..."
else
  echo "Image $IMAGE_NAME not found. Building it..."
  docker build -t "$IMAGE_NAME" .
fi

# Run the Docker container
docker run -p 8080:8080 "$IMAGE_NAME"

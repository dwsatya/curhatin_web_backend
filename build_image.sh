#!/bin/bash

# Set a name for your image (replace with your desired name)
IMAGE_NAME="my-api-flask-app"

# Define the base image (replace with desired Python version)
BASE_IMAGE="python:3.9-slim-buster"

# Create the Dockerfile
cat << EOF > Dockerfile
FROM ${BASE_IMAGE}

WORKDIR /app

# Install dependencies (replace with your requirements file)
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy your application code
COPY . .

# Define the command to run the app (replace with your entrypoint)
CMD [ "python", "app.py" ]
EOF

# Build the Docker image
docker build -t ${IMAGE_NAME} .

echo "Successfully built image: ${IMAGE_NAME}"

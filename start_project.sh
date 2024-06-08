#!/bin/bash

# Function to check if Docker daemon is running
check_docker() {
    echo "Checking if Docker is running..."
    docker info >/dev/null 2>&1
}

# Function to start Docker if it's not running
start_docker() {
    echo "Starting Docker..."

    # For Linux (systemd):
    sudo systemctl start docker

    # Wait for Docker to start and be ready
    echo "Waiting for Docker to launch..."
    while ! docker info >/dev/null 2>&1; do
        sleep 1
    done
}

# Check Docker and start if not running
if ! check_docker; then
    start_docker
else
    echo "Docker is already running."
fi

# Start the project using Docker Compose
echo "Starting the project using Docker Compose..."
docker-compose up --build

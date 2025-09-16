#!/bin/bash
# setup.sh

echo "Setting up Academic Tutor Assistant..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create data directory if it doesn't exist
mkdir -p data

# Create storage directory if it doesn't exist
mkdir -p storage

# Check if .env file exists
if [ ! -f .env ]; then
    echo "Creating .env file from template..."
    cp .env.template .env
    echo "Please update the .env file with your API keys."
fi

echo "Setup complete! You can now run 'docker-compose up --build' to start the application."
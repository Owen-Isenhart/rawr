#!/bin/bash
set -e

echo "Building rawr-agent Docker image..."
cd "$(dirname "$0")/.."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
  echo "Error: Docker is not running."
  exit 1
fi

# Build image
docker build -f Dockerfile.agent -t rawr-agent:latest .

echo "Build complete: rawr-agent:latest"

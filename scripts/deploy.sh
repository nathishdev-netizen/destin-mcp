#!/bin/bash

# Destin MCP Server Deployment Script
set -e

echo "🚀 Starting Destin MCP Server Deployment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Build and start the services
print_status "Building Docker image..."
docker-compose build

print_status "Starting services..."
docker-compose up -d

# Wait for services to be healthy
print_status "Waiting for services to be healthy..."
sleep 10

# Check service status
if docker-compose ps | grep -q "Up"; then
    print_status "✅ Destin MCP Server is running successfully!"
    print_status "Container status:"
    docker-compose ps
else
    print_error "❌ Failed to start services"
    print_error "Logs:"
    docker-compose logs
    exit 1
fi

print_status "🎉 Deployment completed successfully!"
print_status "To view logs: docker-compose logs -f"
print_status "To stop: docker-compose down"

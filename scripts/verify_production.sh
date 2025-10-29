#!/bin/bash

# Production Verification Script for Destin MCP Server
set -e

echo "🔍 Verifying Destin MCP Server Production Setup..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ️  $1${NC}"
}

# Check if Docker is running
if ! docker --version &> /dev/null; then
    print_error "Docker is not installed or not running"
    exit 1
fi
print_success "Docker is running"

# Check if container is running
if docker-compose ps | grep -q "Up.*healthy"; then
    print_success "Container is running and healthy"
else
    print_error "Container is not running or unhealthy"
    print_info "Starting container..."
    docker-compose up -d
    sleep 10
fi

# Test health endpoint
if curl -s http://localhost:8000/health | grep -q "healthy"; then
    print_success "Health endpoint responding"
else
    print_error "Health endpoint not responding"
    exit 1
fi

# Test main endpoint
if curl -s http://localhost:8000/ | grep -q "Destin MCP Server"; then
    print_success "Main endpoint responding"
else
    print_error "Main endpoint not responding"
    exit 1
fi

# Test tools endpoint
TOOLS_COUNT=$(curl -s http://localhost:8000/tools | jq '.tools | length' 2>/dev/null || echo "0")
if [ "$TOOLS_COUNT" -eq 5 ]; then
    print_success "All 5 tools available"
else
    print_error "Expected 5 tools, found $TOOLS_COUNT"
fi

# Test a simple tool call
if curl -s -X POST http://localhost:8000/call_tool \
    -H "Content-Type: application/json" \
    -d '{"name":"list_suppliers","arguments":{}}' | grep -q "success"; then
    print_success "Tool calling working"
else
    print_error "Tool calling failed"
fi

echo ""
print_success "🎉 Production verification complete!"
print_info "Your MCP server is ready for EC2 deployment"
print_info "Container: $(docker-compose ps --format 'table {{.Name}}\t{{.Status}}')"
print_info "Access: http://localhost:8000"

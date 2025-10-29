# 🐳 Docker Quick Start Guide

## What is Docker? (Simple Explanation)

Think of Docker like a **shipping container** for your application:
- **Container**: A box that contains everything your app needs to run
- **Image**: The blueprint/recipe to create containers
- **Dockerfile**: Instructions on how to build the image

## Local Testing (Before EC2)

### 1. Install Docker Desktop
- Download from [docker.com](https://www.docker.com/products/docker-desktop/)
- Install and start Docker Desktop

### 2. Test Your Container Locally
```bash
# Navigate to your project
cd /Users/nathish/Desktop/Nathish/tt/destin_mcp_server

# Build the Docker image
docker build -t destin-mcp-server .

# Run the container
docker run -d --name mcp-server -p 8000:8000 destin-mcp-server

# Check if it's running
docker ps

# View logs
docker logs mcp-server

# Stop the container
docker stop mcp-server
docker rm mcp-server
```

### 3. Use Docker Compose (Easier)
```bash
# Start everything
docker-compose up -d

# View logs
docker-compose logs -f

# Stop everything
docker-compose down
```

## Understanding the Files

### Dockerfile
```dockerfile
FROM python:3.11-slim    # Base image (like Ubuntu with Python)
WORKDIR /app             # Set working directory inside container
COPY . .                 # Copy your code into container
RUN pip install -r requirements.txt  # Install dependencies
CMD ["python", "main.py"] # Command to run when container starts
```

### docker-compose.yml
```yaml
services:
  destin-mcp-server:     # Service name
    build: .             # Build from Dockerfile in current directory
    ports:
      - "8000:8000"      # Map port 8000 from container to host
    restart: unless-stopped  # Auto-restart if it crashes
```

## Common Docker Commands

```bash
# Images
docker images                    # List all images
docker build -t myapp .         # Build image from Dockerfile
docker rmi image_name           # Remove image

# Containers
docker ps                       # List running containers
docker ps -a                    # List all containers
docker run image_name           # Run container from image
docker stop container_name      # Stop container
docker rm container_name        # Remove container
docker logs container_name      # View container logs

# Docker Compose
docker-compose up              # Start services
docker-compose up -d           # Start in background
docker-compose down            # Stop and remove services
docker-compose logs            # View logs
docker-compose ps              # List services
```

## Troubleshooting

### Container Won't Start
```bash
# Check logs
docker logs container_name

# Run interactively to debug
docker run -it destin-mcp-server /bin/bash
```

### Port Already in Use
```bash
# Find what's using the port
lsof -i :8000

# Kill the process
kill -9 PID
```

### Permission Issues
```bash
# Fix file permissions
chmod +x scripts/deploy.sh
```

## Next Steps

1. ✅ Test locally with Docker
2. ✅ Create AWS EC2 instance
3. ✅ Deploy to EC2
4. ✅ Set up domain and SSL
5. ✅ Monitor and maintain

Your MCP server is now ready for production! 🚀

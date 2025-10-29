# 🚀 EC2 Deployment Guide for Destin MCP Server

## Prerequisites
- AWS Account
- Basic understanding of SSH
- Your project files ready

## Step 1: Launch EC2 Instance

### 1.1 Go to AWS Console
- Login to [AWS Console](https://console.aws.amazon.com/)
- Navigate to EC2 service
- Click "Launch Instance"

### 1.2 Configure Instance
```
Name: destin-mcp-server
AMI: Ubuntu Server 22.04 LTS (Free Tier)
Instance Type: t2.micro (Free Tier) or t3.small (Recommended)
Key Pair: Create new or use existing
Security Group: Create new with these rules:
  - SSH (22): Your IP
  - HTTP (80): 0.0.0.0/0
  - HTTPS (443): 0.0.0.0/0
  - Custom TCP (8000): 0.0.0.0/0 (for MCP server)
Storage: 8-20 GB (default is fine)
```

### 1.3 Launch Instance
- Review settings
- Click "Launch Instance"
- Wait for instance to be "Running"

## Step 2: Connect to EC2 Instance

### 2.1 Get Connection Details
- Select your instance
- Click "Connect"
- Copy the SSH command

### 2.2 Connect via SSH
```bash
# Example (replace with your details)
ssh -i "your-key.pem" ubuntu@ec2-xx-xx-xx-xx.compute-1.amazonaws.com
```

## Step 3: Setup Server Environment

### 3.1 Update System
```bash
sudo apt update && sudo apt upgrade -y
```

### 3.2 Install Docker
```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add user to docker group
sudo usermod -aG docker ubuntu

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Logout and login again for group changes
exit
# SSH back in
```

### 3.3 Install Git
```bash
sudo apt install git -y
```

## Step 4: Deploy Your Application

### 4.1 Upload Your Code
**Option A: Using Git (Recommended)**
```bash
# Clone your repository
git clone https://github.com/yourusername/destin_mcp_server.git
cd destin_mcp_server
```

**Option B: Using SCP (if no Git repo)**
```bash
# From your local machine
scp -i "your-key.pem" -r /Users/nathish/Desktop/Nathish/tt/destin_mcp_server ubuntu@your-ec2-ip:~/
```

### 4.2 Deploy with Docker
```bash
# Navigate to project directory
cd destin_mcp_server

# Run deployment script
./scripts/deploy.sh
```

## Step 5: Configure Domain (Optional)

### 5.1 Get Domain Name
- Purchase domain from Route 53 or external provider
- Create A record pointing to your EC2 public IP

### 5.2 Setup SSL with Let's Encrypt
```bash
# Install Certbot
sudo apt install certbot -y

# Get SSL certificate
sudo certbot certonly --standalone -d yourdomain.com
```

## Step 6: Setup Reverse Proxy with Nginx

### 6.1 Install Nginx
```bash
sudo apt install nginx -y
```

### 6.2 Configure Nginx
```bash
sudo nano /etc/nginx/sites-available/destin-mcp
```

Add this configuration:
```nginx
server {
    listen 80;
    server_name yourdomain.com;  # Replace with your domain

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 6.3 Enable Site
```bash
sudo ln -s /etc/nginx/sites-available/destin-mcp /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## Step 7: Setup Auto-Start

### 7.1 Create Systemd Service
```bash
sudo nano /etc/systemd/system/destin-mcp.service
```

Add this content:
```ini
[Unit]
Description=Destin MCP Server
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/home/ubuntu/destin_mcp_server
ExecStart=/usr/local/bin/docker-compose up -d
ExecStop=/usr/local/bin/docker-compose down
User=ubuntu

[Install]
WantedBy=multi-user.target
```

### 7.2 Enable Service
```bash
sudo systemctl daemon-reload
sudo systemctl enable destin-mcp.service
sudo systemctl start destin-mcp.service
```

## Step 8: Monitoring and Maintenance

### 8.1 Check Status
```bash
# Check container status
docker-compose ps

# View logs
docker-compose logs -f

# Check system resources
htop
df -h
```

### 8.2 Update Application
```bash
# Pull latest changes
git pull

# Rebuild and restart
docker-compose down
docker-compose build
docker-compose up -d
```

## Troubleshooting

### Common Issues
1. **Permission Denied**: Check file permissions and user groups
2. **Port Already in Use**: Check what's using the port with `sudo netstat -tulpn`
3. **Out of Memory**: Upgrade to larger instance type
4. **SSL Issues**: Check domain DNS and certificate validity

### Useful Commands
```bash
# View all containers
docker ps -a

# View container logs
docker logs container_name

# Access container shell
docker exec -it container_name /bin/bash

# Check disk space
df -h

# Check memory usage
free -h

# Check running processes
ps aux
```

## Security Best Practices

1. **Firewall**: Only open necessary ports
2. **SSH Keys**: Use key-based authentication, disable password auth
3. **Updates**: Keep system and packages updated
4. **Backups**: Regular backups of important data
5. **Monitoring**: Set up CloudWatch or other monitoring
6. **SSL**: Always use HTTPS in production

## Cost Optimization

1. **Instance Type**: Start with t2.micro (free tier)
2. **Reserved Instances**: For long-term use
3. **Auto Scaling**: Scale based on demand
4. **Spot Instances**: For non-critical workloads
5. **CloudWatch**: Monitor and optimize resource usage

---

🎉 **Your Destin MCP Server is now running on AWS EC2!**

Access your server at: `http://your-ec2-public-ip:8000`
Or with domain: `https://yourdomain.com`

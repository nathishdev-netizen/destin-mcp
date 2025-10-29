# 🔗 Claude Desktop Integration Guide

## Overview

Your Destin MCP Server now supports **two integration methods** with Claude Desktop:

1. **🏠 Local Integration** (STDIO) - For development and local use
2. **☁️ Remote Integration** (MCP-over-HTTP) - For Claude Desktop Pro Custom Connectors

## 🏠 Local Integration (STDIO Mode)

### For Claude Desktop (Free/Pro)

**Step 1: Configure Claude Desktop**
```json
{
  "mcpServers": {
    "destin-travel": {
      "command": "python",
      "args": ["/Users/nathish/Desktop/Nathish/tt/destin_mcp_server/main.py"],
      "env": {
        "PYTHONPATH": "/Users/nathish/Desktop/Nathish/tt/destin_mcp_server/src"
      }
    }
  }
}
```

**Step 2: Save Configuration**
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

**Step 3: Restart Claude Desktop**

## ☁️ Remote Integration (Claude Desktop Pro)

### For Claude Desktop Pro Custom Connectors

**Step 1: Deploy to AWS EC2**
```bash
# Deploy with MCP-over-HTTP mode
docker-compose -f docker-compose.mcp-http.yml up -d
```

**Step 2: Get Your Server URL**
After EC2 deployment, your server will be available at:
```
https://your-ec2-domain.com
# or
http://your-ec2-ip:8000
```

**Step 3: Add Custom Connector in Claude Desktop Pro**

1. **Open Claude Desktop Pro**
2. **Go to Settings** → **Connectors**
3. **Click "Add custom connector"**
4. **Enter your server URL**: `https://your-ec2-domain.com`
5. **Click "Add"**

### Server URL Examples
- **With Domain**: `https://destin-mcp.yourdomain.com`
- **With IP**: `http://54.123.45.67:8000`
- **With SSL**: `https://your-ec2-domain.amazonaws.com`

## 🚀 Deployment Modes

### Mode 1: STDIO (Local)
```bash
# Run locally for Claude Desktop config
python main.py
```

### Mode 2: HTTP REST API
```bash
# Run as REST API server
docker-compose up -d
```

### Mode 3: MCP-over-HTTP (Claude Pro)
```bash
# Run for Claude Desktop Pro Custom Connectors
docker-compose -f docker-compose.mcp-http.yml up -d
```

## 🔍 Testing Your Setup

### Test Local STDIO Mode
```bash
# Test with MCP Inspector
npx @modelcontextprotocol/inspector python main.py
```

### Test MCP-over-HTTP Mode
```bash
# Test MCP protocol endpoints
python scripts/test_mcp_http.py

# Test server info
curl http://localhost:8000/

# Test MCP initialize
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}'
```

## 📋 Available Tools in Claude

Once connected, you'll have access to these tools in Claude:

1. **🔍 search_hotels** - Search for hotels with real-time pricing
2. **🏨 book_hotel** - Complete hotel booking with confirmation
3. **ℹ️ get_hotel_info** - Detailed hotel information and amenities
4. **📋 get_booking_details** - Retrieve existing booking information
5. **🏢 list_suppliers** - Available hotel booking suppliers

## 🌐 Example Usage in Claude

**Hotel Search:**
```
"Find hotels in Mumbai for December 21-24, 2025 for 2 adults"
```

**Hotel Booking:**
```
"Book the Pride Plaza Hotel for those dates with guest details:
- John Smith (Mr.)
- Contact: john@email.com, +1234567890"
```

## 🔧 Troubleshooting

### Local Integration Issues
- ✅ Check Python path in config
- ✅ Ensure virtual environment is activated
- ✅ Verify file permissions
- ✅ Check Claude Desktop logs

### Remote Integration Issues
- ✅ Verify server is accessible: `curl http://your-server/health`
- ✅ Check CORS headers for Claude domains
- ✅ Ensure HTTPS for production (recommended)
- ✅ Verify MCP protocol endpoints: `/mcp` and `/sse/{id}`

### Common Solutions
```bash
# Check server status
docker-compose -f docker-compose.mcp-http.yml ps

# View server logs
docker-compose -f docker-compose.mcp-http.yml logs -f

# Test MCP endpoints
python scripts/test_mcp_http.py

# Restart server
docker-compose -f docker-compose.mcp-http.yml restart
```

## 🎯 Production Deployment

### For Claude Desktop Pro (Recommended)

1. **Deploy to AWS EC2** with MCP-over-HTTP mode
2. **Setup SSL/HTTPS** (recommended for security)
3. **Configure domain** (optional but professional)
4. **Add to Claude Pro** as Custom Connector

### SSL Setup (Optional)
```bash
# Install Certbot
sudo apt install certbot

# Get SSL certificate
sudo certbot certonly --standalone -d yourdomain.com

# Configure Nginx reverse proxy (see EC2_DEPLOYMENT_GUIDE.md)
```

## 📞 Support

- **Local Issues**: Check Claude Desktop documentation
- **Remote Issues**: Verify server deployment and MCP protocol compliance
- **Tool Issues**: Check server logs and API responses

---

🎉 **Your Destin MCP Server is now ready for both local and remote Claude Desktop integration!**

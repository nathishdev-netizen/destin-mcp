# 🚀 Destin MCP Server - Professional Travel Tech Integration

A **production-ready** Model Context Protocol (MCP) server with professional architecture for integrating travel booking APIs with AI assistants like Claude.

## 🎯 Overview

This MCP server transforms complex travel booking APIs into an intelligent, conversational interface that makes hotel booking as easy as having a conversation with a professional travel agent. It provides AI assistants with comprehensive hotel search, booking, and management capabilities through the Destin travel tech platform.

## 🏗️ Professional Architecture

```
src/destin_mcp/              # 📦 Main Package
├── tools/                   # 🔧 MCP Tools (5 hotel operations)
├── resources/               # 📚 Documentation & Guides (6 resources)
├── prompts/                 # 🤖 AI Assistant Templates (4 prompts)
├── models/                  # 📊 Type-safe Data Models
├── utils/                   # 🛠️ HTTP Client & Logging
├── config/                  # ⚙️ Environment Settings
└── server.py                # 🖥️ Main MCP Server
```

## 🔧 Enhanced Tools with Detailed Descriptions

### **1. 🔍 HOTEL SEARCH ENGINE** (`search_hotels`)
**Advanced hotel discovery with real-time pricing across multiple suppliers**
- Searches thousands of hotels globally with live inventory
- Supports complex occupancy (families, groups, business travelers)
- Multi-supplier comparison (DIDA, GOGLOBAL)
- Returns booking codes for instant reservation

### **2. 🏨 HOTEL BOOKING SYSTEM** (`book_hotel`)
**Complete reservation management with instant confirmation**
- Processes multiple rooms and guest configurations
- Instant booking confirmation with reference numbers
- Automatic price calculation including taxes and fees
- Real-time inventory management and allocation

### **3. ℹ️ HOTEL INFORMATION CENTER** (`get_hotel_info`)
**Comprehensive property intelligence and amenity details**
- Complete hotel profiles with descriptions and policies
- Detailed facility listings (pools, gyms, restaurants, etc.)
- Room configurations and service offerings
- Location details and accessibility information

### **4. 📋 BOOKING MANAGEMENT SYSTEM** (`get_booking_details`)
**Complete booking lifecycle management and status tracking**
- Real-time booking status and confirmations
- Complete guest information and room assignments
- Pricing breakdown and payment details
- Cancellation policies and modification options

### **5. 🏢 SUPPLIER NETWORK DIRECTORY** (`list_suppliers`)
**Comprehensive supplier intelligence and capability comparison**
- Complete supplier directory with coverage areas
- Feature comparisons and specializations
- Integration status and reliability metrics
- Recommendations for specific use cases

## 🤖 AI-Powered Prompts

### **1. 🔍 hotel-search-assistant**
Intelligent hotel search guidance that transforms natural language into structured searches

### **2. 📋 booking-confirmation-assistant**
Booking management support for reservations and policy questions

### **3. 🗺️ travel-planning-assistant**
Comprehensive trip planning with context-aware recommendations

### **4. 🔄 hotel-comparison-assistant**
Intelligent hotel comparison and decision-making support

## 📚 Comprehensive Resources

- **API Integration Guide** - Complete documentation and examples
- **Hotel Booking Guide** - Step-by-step booking procedures
- **Supplier Information** - Detailed supplier profiles and capabilities
- **Server Configuration** - Current settings and customization options
- **Request Examples** - JSON templates for all operations

## Installation

### Prerequisites

- Python 3.8+
- pip package manager

### Setup

1. **Clone/Download the project:**
   ```bash
   cd /path/to/destin_mcp_server
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Make the server executable:**
   ```bash
   chmod +x server.py
   ```

## Configuration

### Environment Variables (Optional)

Create a `.env` file for custom configuration:

```env
# API Configuration
BASE_URL=https://supplier-apis-for-travel-tech.vercel.app
DEFAULT_SUPPLIER=dida
TIMEOUT_SECONDS=30

# Logging
LOG_LEVEL=INFO
```

### Supplier Configuration

The server supports multiple hotel suppliers:
- **DIDA** (default): `dida`
- **GOGLOBAL**: `goglobal`

## Usage

### Running the Server

```bash
python server.py
```

### Testing with MCP Inspector

1. **Install MCP Inspector:**
   ```bash
   npm install -g @modelcontextprotocol/inspector
   ```

2. **Run the inspector:**
   ```bash
   mcp-inspector python server.py
   ```

3. **Open your browser** to the provided URL to test the tools interactively.

## 🚀 Deployment Modes

### 🏠 Local Integration (STDIO Mode)
For Claude Desktop local configuration:
```bash
# Run locally for Claude Desktop
python main.py
```

**Claude Desktop Configuration:**
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

### 🌐 REST API Mode
For web applications and API access:
```bash
# Run as HTTP REST API server
docker-compose up -d

# Test endpoints
curl http://localhost:8000/health
curl http://localhost:8000/tools
```

### ☁️ Claude Desktop Pro Mode (MCP-over-HTTP)
For Claude Desktop Pro Custom Connectors:
```bash
# Run for Claude Desktop Pro Custom Connectors
docker-compose -f docker-compose.mcp-http.yml up -d

# Test MCP protocol
python scripts/test_mcp_http.py
```

**Add to Claude Desktop Pro:**
1. Go to Settings → Connectors
2. Click "Add custom connector"
3. Enter your server URL: `https://your-ec2-domain.com`
4. Click "Add"

### Integration with Claude Desktop

## API Examples

### Search Hotels

```json
{
  "country": "IN",
  "fromDate": "2024-12-15",
  "toDate": "2024-12-18",
  "cityCode": "75",
  "currency": "USD",
  "occupancy": [
    {
      "adults": 2,
      "roomCount": 1
    }
  ],
  "supplier": "dida"
}
```

### Book Hotel

```json
{
  "country": "IN",
  "currency": "USD",
  "fromDate": "2024-12-15",
  "toDate": "2024-12-18",
  "roomCode": "26323492/5862457869987957513/575",
  "rooms": [
    {
      "adults": 2,
      "guests": [
        {
          "title": "MR.",
          "firstName": "JOHN",
          "lastName": "DOE"
        },
        {
          "title": "MRS.",
          "firstName": "JANE",
          "lastName": "DOE"
        }
      ]
    }
  ],
  "supplier": "dida"
}
```

## Architecture

### Production Features

- **🔒 Input Validation**: Comprehensive Pydantic models for type safety
- **⚡ Async Operations**: Full async/await support for high performance
- **🛡️ Error Handling**: Robust error handling with detailed logging
- **📊 Logging**: Structured logging for monitoring and debugging
- **🔄 HTTP Client Management**: Proper connection pooling and timeouts
- **📋 Schema Validation**: JSON Schema validation for all tool inputs
- **🎯 Type Safety**: Full type hints throughout the codebase

### Code Structure

```
destin_mcp_server/
├── server.py              # Main MCP server implementation
├── requirements.txt       # Python dependencies
├── README.md              # This documentation
└── .env                   # Environment configuration (optional)
```

## Error Handling

The server implements comprehensive error handling:

- **HTTP Errors**: Proper status code handling and error messages
- **Validation Errors**: Clear validation error messages with field details
- **Network Errors**: Timeout and connection error handling
- **API Errors**: Structured error responses from travel APIs

## Logging

Structured logging is implemented throughout:

```python
# Log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
logger.info("Making POST request to /api/hotels/dida")
logger.error("HTTP 400: Invalid request parameters")
```

## Security Considerations

- **Input Sanitization**: All inputs are validated using Pydantic models
- **Request Timeouts**: Configurable timeouts prevent hanging requests
- **Error Information**: Sensitive information is not exposed in error messages
- **Type Safety**: Strong typing prevents injection attacks

## Troubleshooting

### Common Issues

1. **Connection Errors**
   - Check internet connectivity
   - Verify BASE_URL is accessible
   - Check firewall settings

2. **Validation Errors**
   - Ensure date formats are YYYY-MM-DD
   - Check required fields are provided
   - Verify data types match schema

3. **API Errors**
   - Check supplier availability
   - Verify API endpoints are functional
   - Review request parameters

### Debug Mode

Enable debug logging:

```python
logging.basicConfig(level=logging.DEBUG)
```

## Contributing

1. Follow PEP 8 style guidelines
2. Add type hints to all functions
3. Include comprehensive error handling
4. Update documentation for new features
5. Add tests for new functionality

## License

This project is licensed under the MIT License.

## Support

For issues and questions:
- Check the troubleshooting section
- Review the MCP documentation: https://modelcontextprotocol.io/
- Open an issue in the project repository

---

**Built with ❤️ for the travel tech community**

"""Travel-related MCP resources."""

from typing import Any, Dict, List

from mcp.types import Resource, ResourceContents, TextResourceContents

from ..config import get_settings
from ..utils import setup_logger

logger = setup_logger(__name__)


class TravelResources:
    """Travel booking resources and documentation."""
    
    def __init__(self):
        self.settings = get_settings()
    
    def get_resource_list(self) -> List[Resource]:
        """Return list of available resources."""
        return [
            Resource(
                uri="destin://docs/api-guide",
                name="API Integration Guide",
                description="Complete guide for using Destin travel APIs",
                mimeType="text/markdown"
            ),
            Resource(
                uri="destin://docs/hotel-booking",
                name="Hotel Booking Guide",
                description="Step-by-step guide for hotel bookings",
                mimeType="text/markdown"
            ),
            Resource(
                uri="destin://docs/suppliers",
                name="Supplier Information",
                description="Information about available hotel suppliers",
                mimeType="text/markdown"
            ),
            Resource(
                uri="destin://config/settings",
                name="Server Configuration",
                description="Current server configuration and settings",
                mimeType="application/json"
            ),
            Resource(
                uri="destin://examples/search-request",
                name="Hotel Search Example",
                description="Example hotel search request",
                mimeType="application/json"
            ),
            Resource(
                uri="destin://examples/booking-request",
                name="Hotel Booking Example", 
                description="Example hotel booking request",
                mimeType="application/json"
            )
        ]
    
    async def get_resource_contents(self, uri: str) -> ResourceContents:
        """Get contents of a specific resource."""
        if uri == "destin://docs/api-guide":
            return TextResourceContents(
                uri=uri,
                mimeType="text/markdown",
                text=self._get_api_guide()
            )
        elif uri == "destin://docs/hotel-booking":
            return TextResourceContents(
                uri=uri,
                mimeType="text/markdown",
                text=self._get_booking_guide()
            )
        elif uri == "destin://docs/suppliers":
            return TextResourceContents(
                uri=uri,
                mimeType="text/markdown",
                text=self._get_suppliers_info()
            )
        elif uri == "destin://config/settings":
            return TextResourceContents(
                uri=uri,
                mimeType="application/json",
                text=self._get_config_json()
            )
        elif uri == "destin://examples/search-request":
            return TextResourceContents(
                uri=uri,
                mimeType="application/json",
                text=self._get_search_example()
            )
        elif uri == "destin://examples/booking-request":
            return TextResourceContents(
                uri=uri,
                mimeType="application/json",
                text=self._get_booking_example()
            )
        else:
            raise ValueError(f"Unknown resource URI: {uri}")
    
    def _get_api_guide(self) -> str:
        """Get API integration guide."""
        return """# Destin Travel API Integration Guide

## Overview
The Destin MCP Server provides access to travel booking APIs through a standardized Model Context Protocol interface.

## Available Tools

### 1. search_hotels
Search for available hotels based on location, dates, and occupancy.

**Required Parameters:**
- `country`: Country code (e.g., "IN")
- `fromDate`: Check-in date (YYYY-MM-DD)
- `toDate`: Check-out date (YYYY-MM-DD)
- `occupancy`: Array of room occupancy details

**Optional Parameters:**
- `cityCode`: Destination city code
- `currency`: Currency code (default: USD)
- `supplier`: Hotel supplier (default: dida)

### 2. book_hotel
Book a hotel room with complete guest details.

**Required Parameters:**
- `country`: Country code
- `fromDate`: Check-in date
- `toDate`: Check-out date
- `roomCode`: Room code from search results
- `rooms`: Array of room and guest details

### 3. get_hotel_info
Get detailed information about a specific hotel.

**Required Parameters:**
- `hotelId`: Hotel ID from search results
- `country`: Country code
- `fromDate`: Check-in date
- `toDate`: Check-out date
- `occupancy`: Room occupancy details

### 4. get_booking_details
Retrieve details of an existing booking.

**Required Parameters:**
- `bookingId`: Booking ID from confirmation

### 5. list_suppliers
Get list of available hotel suppliers.

**No parameters required.**

## Error Handling
All tools include comprehensive error handling with detailed error messages for troubleshooting.

## Rate Limiting
The server implements rate limiting to ensure fair usage and API stability.
"""
    
    def _get_booking_guide(self) -> str:
        """Get hotel booking guide."""
        return """# Hotel Booking Guide

## Step-by-Step Booking Process

### Step 1: Search for Hotels
Use the `search_hotels` tool to find available hotels:

```json
{
  "country": "IN",
  "fromDate": "2024-12-15",
  "toDate": "2024-12-18",
  "occupancy": [
    {
      "adults": 2,
      "roomCount": 1
    }
  ]
}
```

### Step 2: Review Search Results
The search will return hotels with:
- Hotel ID and name
- Room pricing and availability
- Room codes for booking
- Supplier information

### Step 3: Get Hotel Details (Optional)
Use `get_hotel_info` to get detailed information about a specific hotel.

### Step 4: Book the Hotel
Use the `book_hotel` tool with:
- Room code from search results
- Complete guest information
- Booking dates and details

### Step 5: Confirm Booking
The booking response will include:
- Booking ID and reference
- Confirmation details
- Total price and currency
- Booking status

### Step 6: Retrieve Booking Details
Use `get_booking_details` anytime to check booking status and information.

## Guest Information Requirements
- Title (MR., MRS., MS., etc.)
- First name and last name
- One guest entry per person in the room

## Important Notes
- Dates must be in YYYY-MM-DD format
- Check-out date must be after check-in date
- Room codes are unique to each search session
- Booking confirmations are immediate
"""
    
    def _get_suppliers_info(self) -> str:
        """Get suppliers information."""
        return """# Hotel Suppliers Information

## Available Suppliers

### DIDA (Default)
- **Code**: `dida`
- **Description**: Primary hotel supplier with extensive inventory
- **Coverage**: Global hotel network
- **Features**: Real-time availability, instant booking

### GOGLOBAL
- **Code**: `goglobal`
- **Description**: Secondary supplier for additional inventory
- **Coverage**: International hotels
- **Features**: Competitive pricing, diverse options

## Supplier Selection
- Default supplier is automatically used if not specified
- You can specify a different supplier in tool parameters
- Each supplier may have different hotel availability
- Pricing and terms may vary between suppliers

## API Endpoints
All suppliers use the same API structure:
- Search: `/api/hotels/{supplier}`
- Booking: `/api/hotels/{supplier}/booking`
- Hotel Info: `/api/hotels/{supplier}/{hotelId}`
- Booking Details: `/api/hotels/{supplier}/booking/{bookingId}`

## Supplier Capabilities
Use the `list_suppliers` tool to get current supplier availability and status.
"""
    
    def _get_config_json(self) -> str:
        """Get current configuration as JSON."""
        import json
        config = {
            "server_name": self.settings.server_name,
            "server_version": self.settings.server_version,
            "base_url": self.settings.base_url,
            "default_supplier": self.settings.default_supplier,
            "timeout_seconds": self.settings.timeout_seconds,
            "log_level": self.settings.log_level,
            "debug": self.settings.debug
        }
        return json.dumps(config, indent=2)
    
    def _get_search_example(self) -> str:
        """Get hotel search example."""
        return """{
  "country": "IN",
  "fromDate": "2024-12-15",
  "toDate": "2024-12-18",
  "cityCode": "75",
  "currency": "USD",
  "occupancy": [
    {
      "adults": 2,
      "roomCount": 1
    },
    {
      "adults": 1,
      "roomCount": 1,
      "childAges": [9, 5]
    }
  ],
  "supplier": "dida"
}"""
    
    def _get_booking_example(self) -> str:
        """Get hotel booking example."""
        return """{
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
}"""

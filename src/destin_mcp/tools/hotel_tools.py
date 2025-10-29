"""Hotel-related MCP tools."""

from typing import Any, Dict, List

from mcp.types import CallToolResult, TextContent, Tool

from ..config import get_settings
from ..models import HotelBookingModel, HotelSearchModel
from ..utils import setup_logger
from .base import BaseTool

logger = setup_logger(__name__)


class HotelTools(BaseTool):
    """Hotel booking and search tools."""
    
    def __init__(self, http_client):
        super().__init__(http_client)
        self.settings = get_settings()
    
    def get_tool_definitions(self) -> List[Tool]:
        """Return hotel tool definitions."""
        return [
            Tool(
                name="search_hotels",
                description="""🔍 **HOTEL SEARCH ENGINE**

**IMPORTANT FOR AI ASSISTANTS**: When users ask about hotels, be conversational! Don't immediately show technical JSON. Instead:

1. **Ask Natural Questions First**:
   - "Which city would you like to stay in?"
   - "What are your check-in and check-out dates?"
   - "How many guests will be staying?"
   - "Any preferences for budget or amenities?"

2. **Then Map to Technical Parameters**:
   - Convert city names to codes (Mumbai→BOM, Delhi→DEL, etc.)
   - Format dates as YYYY-MM-DD
   - Structure occupancy properly
   - Use defaults: currency=USD, supplier=dida

**Purpose**: Search and discover available hotels with real-time pricing and availability.

**What it does**:
- Searches thousands of hotels across global destinations
- Provides real-time pricing in USD
- Shows room availability for specific dates and guest configurations
- Returns detailed hotel information including amenities and location
- Supports multiple room types and guest combinations

**City Code Reference**:
- Mumbai/Bombay → BOM
- Delhi/New Delhi → DEL  
- Bangalore/Bengaluru → BLR
- Chennai/Madras → MAA
- Kolkata/Calcutta → CCU

**Returns**: List of available hotels with pricing, room details, supplier info, and booking codes.""",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "country": {
                            "type": "string",
                            "description": "Country code (e.g., 'IN')",
                            "minLength": 2,
                            "maxLength": 2
                        },
                        "fromDate": {
                            "type": "string",
                            "description": "Check-in date in YYYY-MM-DD format",
                            "pattern": "^\\d{4}-\\d{2}-\\d{2}$"
                        },
                        "toDate": {
                            "type": "string",
                            "description": "Check-out date in YYYY-MM-DD format",
                            "pattern": "^\\d{4}-\\d{2}-\\d{2}$"
                        },
                        "cityCode": {
                            "type": "string",
                            "description": "City code for the destination"
                        },
                        "currency": {
                            "type": "string",
                            "description": "Currency code (default: USD)",
                            "default": "USD"
                        },
                        "occupancy": {
                            "type": "array",
                            "description": "Room occupancy details",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "adults": {
                                        "type": "integer",
                                        "minimum": 1,
                                        "maximum": 10,
                                        "description": "Number of adults"
                                    },
                                    "roomCount": {
                                        "type": "integer",
                                        "minimum": 1,
                                        "maximum": 5,
                                        "description": "Number of rooms"
                                    },
                                    "childAges": {
                                        "type": "array",
                                        "items": {"type": "integer"},
                                        "description": "Ages of children"
                                    }
                                },
                                "required": ["adults", "roomCount"]
                            }
                        },
                        "supplier": {
                            "type": "string",
                            "description": "Hotel supplier (default: dida)",
                            "default": "dida"
                        }
                    },
                    "required": ["country", "fromDate", "toDate", "occupancy"]
                }
            ),
            Tool(
                name="book_hotel",
                description="""🏨 **HOTEL BOOKING SYSTEM**

**IMPORTANT**: Always include the hotelId from search results when booking!

**Purpose**: Complete hotel reservation system with instant booking confirmation and guest management.

**Required Information**:
- Hotel ID (from search_hotels results)
- Room Code (from search_hotels results)  
- Guest details (title, first name, last name for each guest)
- **Contact object** with Name (First, Last), Email, and Phone
- Check-in and check-out dates
- Country code

**What it does**:
- Creates confirmed hotel reservations with immediate booking references
- Processes guest information and room assignments
- Handles payment processing and booking confirmation
- Generates booking references and confirmation codes
- Manages multiple rooms and guest configurations
- Provides detailed booking status and policies

**Key Features**:
- Instant booking confirmation with reference numbers
- Support for multiple guests per room with individual details
- Automatic price calculation including taxes and fees
- Real-time inventory management and room allocation
- Booking status tracking and management
- Cancellation policy information

**Use cases**:
- Book corporate accommodations for business travelers
- Reserve family rooms with multiple guest configurations
- Create group bookings for events or conferences
- Secure last-minute hotel reservations
- Book accommodations with specific guest requirements

**Returns**: Complete booking confirmation with booking ID, reference number, total cost, hotel details, and guest information.""",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "hotelId": {
                            "type": "string",
                            "description": "Hotel ID from search results (required)"
                        },
                        "country": {
                            "type": "string",
                            "description": "Country code",
                            "minLength": 2,
                            "maxLength": 2
                        },
                        "currency": {
                            "type": "string",
                            "description": "Currency code",
                            "default": "USD"
                        },
                        "fromDate": {
                            "type": "string",
                            "description": "Check-in date in YYYY-MM-DD format",
                            "pattern": "^\\d{4}-\\d{2}-\\d{2}$"
                        },
                        "toDate": {
                            "type": "string",
                            "description": "Check-out date in YYYY-MM-DD format",
                            "pattern": "^\\d{4}-\\d{2}-\\d{2}$"
                        },
                        "roomCode": {
                            "type": "string",
                            "description": "Room code from search results"
                        },
                        "contact": {
                            "type": "object",
                            "description": "Primary contact information for booking",
                            "properties": {
                                "Name": {
                                    "type": "object",
                                    "properties": {
                                        "First": {"type": "string", "description": "Contact first name"},
                                        "Last": {"type": "string", "description": "Contact last name"}
                                    },
                                    "required": ["First", "Last"]
                                },
                                "Email": {"type": "string", "description": "Contact email address"},
                                "Phone": {"type": "string", "description": "Contact phone number"}
                            },
                            "required": ["Name", "Email", "Phone"]
                        },
                        "rooms": {
                            "type": "array",
                            "description": "Room and guest details",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "adults": {
                                        "type": "integer",
                                        "minimum": 1,
                                        "maximum": 10
                                    },
                                    "guests": {
                                        "type": "array",
                                        "items": {
                                            "type": "object",
                                            "properties": {
                                                "title": {"type": "string"},
                                                "firstName": {"type": "string"},
                                                "lastName": {"type": "string"}
                                            },
                                            "required": ["title", "firstName", "lastName"]
                                        }
                                    }
                                },
                                "required": ["adults", "guests"]
                            }
                        },
                        "supplier": {
                            "type": "string",
                            "description": "Hotel supplier",
                            "default": "dida"
                        }
                    },
                    "required": ["hotelId", "country", "fromDate", "toDate", "roomCode", "contact", "rooms"]
                }
            ),
            Tool(
                name="get_hotel_info",
                description="""ℹ️ **HOTEL INFORMATION CENTER**
                
**Purpose**: Comprehensive hotel information system providing detailed property data, amenities, and policies.

**What it does**:
- Retrieves complete hotel profiles with detailed descriptions
- Provides comprehensive amenity and facility listings
- Shows room types, configurations, and features
- Displays hotel policies, check-in/out times, and restrictions
- Includes location information and nearby attractions
- Offers pricing context and value propositions

**Detailed Information Includes**:
- Hotel description and property overview
- Complete facility listings (pool, gym, spa, restaurants, etc.)
- Room amenities and configurations
- Service offerings and guest experiences
- Location details and accessibility information
- Hotel policies and important notices
- Photo galleries and virtual tours (when available)

**Use cases**:
- Research hotel amenities before booking decisions
- Compare facility offerings between properties
- Understand hotel policies and restrictions
- Evaluate location and accessibility features
- Assess value proposition and guest experience quality
- Gather information for travel planning and recommendations

**Returns**: Comprehensive hotel profile with descriptions, amenities, facilities, policies, and location details.""",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "hotelId": {
                            "type": "string",
                            "description": "Hotel ID from search results"
                        },
                        "country": {
                            "type": "string",
                            "description": "Country code",
                            "minLength": 2,
                            "maxLength": 2
                        },
                        "fromDate": {
                            "type": "string",
                            "description": "Check-in date in YYYY-MM-DD format",
                            "pattern": "^\\d{4}-\\d{2}-\\d{2}$"
                        },
                        "toDate": {
                            "type": "string",
                            "description": "Check-out date in YYYY-MM-DD format",
                            "pattern": "^\\d{4}-\\d{2}-\\d{2}$"
                        },
                        "occupancy": {
                            "type": "array",
                            "description": "Room occupancy details",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "adults": {"type": "integer", "minimum": 1},
                                    "roomCount": {"type": "integer", "minimum": 1}
                                },
                                "required": ["adults", "roomCount"]
                            }
                        },
                        "supplier": {
                            "type": "string",
                            "description": "Hotel supplier",
                            "default": "dida"
                        }
                    },
                    "required": ["hotelId", "country", "fromDate", "toDate", "occupancy"]
                }
            ),
            Tool(
                name="get_booking_details",
                description="""📋 **BOOKING MANAGEMENT SYSTEM**
                
**Purpose**: Complete booking information retrieval and management system for existing hotel reservations.

**What it does**:
- Retrieves comprehensive booking details and current status
- Provides real-time booking status updates and confirmations
- Shows complete guest information and room assignments
- Displays pricing breakdown, payment status, and policies
- Offers cancellation and modification policy information
- Tracks booking history and status changes

**Comprehensive Details Include**:
- Booking confirmation number and reference codes
- Current booking status (confirmed, cancelled, modified, etc.)
- Complete guest information and room assignments
- Hotel details, location, and contact information
- Check-in/check-out dates and special instructions
- Total pricing, payment status, and billing information
- Cancellation policies and modification options
- Special requests and preferences
- Booking creation and modification history

**Use cases**:
- Verify booking details before travel
- Check booking status and confirmations
- Review cancellation and modification policies
- Access guest information for check-in purposes
- Resolve booking issues and discrepancies
- Manage corporate travel booking records
- Provide booking information to travel companions

**Returns**: Complete booking record with all details, status, guest information, pricing, and policy information.""",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "bookingId": {
                            "type": "string",
                            "description": "Booking ID from booking confirmation"
                        },
                        "supplier": {
                            "type": "string",
                            "description": "Hotel supplier",
                            "default": "dida"
                        }
                    },
                    "required": ["bookingId"]
                }
            ),
            Tool(
                name="list_suppliers",
                description="""🏢 **SUPPLIER NETWORK DIRECTORY**
                
**Purpose**: Comprehensive directory of available hotel suppliers and booking sources with their capabilities and coverage.

**What it does**:
- Lists all available hotel suppliers and booking platforms
- Provides supplier capabilities and coverage information
- Shows supplier-specific features and advantages
- Displays network size and global coverage details
- Offers integration status and availability information
- Helps choose the best supplier for specific needs

**Supplier Information Includes**:
- Supplier names and identification codes
- Global coverage and regional specializations
- Hotel inventory size and property types
- Booking capabilities and features
- Pricing models and commission structures
- Integration status and API availability
- Special features and unique offerings

**Use cases**:
- Choose the best supplier for specific destinations
- Compare supplier coverage and capabilities
- Understand pricing and inventory differences
- Select suppliers for corporate travel programs
- Evaluate supplier reliability and performance
- Plan multi-supplier booking strategies
- Access specialized inventory and rates

**Returns**: Complete supplier directory with names, codes, capabilities, coverage areas, and feature comparisons.""",
                inputSchema={
                    "type": "object",
                    "properties": {},
                    "additionalProperties": False
                }
            )
        ]
    
    async def execute_tool(self, name: str, arguments: Dict[str, Any]) -> CallToolResult:
        """Execute hotel tool by name."""
        logger.info(f"Executing hotel tool: {name}")
        logger.debug(f"Arguments: {arguments}")
        
        try:
            if name == "search_hotels":
                return await self._search_hotels(arguments)
            elif name == "book_hotel":
                return await self._book_hotel(arguments)
            elif name == "get_hotel_info":
                return await self._get_hotel_info(arguments)
            elif name == "get_booking_details":
                return await self._get_booking_details(arguments)
            elif name == "list_suppliers":
                return await self._list_suppliers(arguments)
            else:
                raise ValueError(f"Unknown hotel tool: {name}")
        except Exception as e:
            logger.error(f"Hotel tool execution failed: {str(e)}")
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=f"Error executing hotel tool: {str(e)}"
                    )
                ],
                isError=True
            )
    
    async def _search_hotels(self, arguments: Dict[str, Any]) -> CallToolResult:
        """Search for hotels based on criteria."""
        # Validate input
        search_data = HotelSearchModel(**arguments)
        supplier = arguments.get("supplier", self.settings.default_supplier)
        
        # Prepare request data
        request_data = search_data.dict(exclude={"supplier"})
        
        # Make API request
        result = await self.http_client.make_request(
            "POST",
            f"/api/hotels/{supplier}",
            request_data,
            supplier
        )
        
        
        # Format response
        if result.get("success") and result.get("data"):
            data = result["data"]
            
            # Check if data is an error response
            if isinstance(data, dict) and "Code" in data and "Message" in data:
                return CallToolResult(
                    content=[TextContent(type="text", text=f"API Error {data['Code']}: {data['Message']}")]
                )
            
            # Check if data is a list of hotels
            if isinstance(data, list):
                hotels = data
                response_text = f"Found {len(hotels)} hotels:\n\n"
                
                for hotel in hotels:
                    response_text += f"🏨 **{hotel.get('name', 'N/A')}**\n"
                    response_text += f"   ID: {hotel.get('id', 'N/A')}\n"
                    response_text += f"   Supplier: {hotel.get('supplier', 'N/A')}\n"
                    
                    if 'rooms' in hotel:
                        room = hotel['rooms']
                        response_text += f"   Price: {room.get('price', 'N/A')} {room.get('currency', 'N/A')}\n"
                        response_text += f"   Room Basis: {room.get('room_basis', 'N/A')}\n"
                        response_text += f"   Room ID: {room.get('id', 'N/A')}\n"
                    
                    response_text += "\n"
                
                return CallToolResult(
                    content=[TextContent(type="text", text=response_text)]
                )
            else:
                return CallToolResult(
                    content=[TextContent(type="text", text=f"Unexpected data format: {type(data)}")]
                )
        else:
            return CallToolResult(
                content=[TextContent(type="text", text="No hotels found for the given criteria.")]
            )
    
    async def _book_hotel(self, arguments: Dict[str, Any]) -> CallToolResult:
        """Book a hotel room."""
        # Validate input
        booking_data = HotelBookingModel(**arguments)
        supplier = arguments.get("supplier", self.settings.default_supplier)
        
        # Prepare request data (exclude only supplier from body, keep hotelId)
        request_data = booking_data.model_dump(exclude={"supplier"})
        
        # Make API request with original URL structure
        result = await self.http_client.make_request(
            "POST",
            f"/api/hotels/{supplier}/booking",
            request_data,
            supplier
        )
        
        # Format response
        if result:
            response_text = "🎉 **Hotel Booking Confirmation**\n\n"
            response_text += f"Booking ID: {result.get('GoBookingCode', 'N/A')}\n"
            response_text += f"Reference: {result.get('GoReference', 'N/A')}\n"
            response_text += f"Hotel: {result.get('HotelName', 'N/A')}\n"
            response_text += f"Total Price: {result.get('TotalPrice', 'N/A')} {result.get('Currency', 'N/A')}\n"
            response_text += f"Arrival Date: {result.get('ArrivalDate', 'N/A')}\n"
            response_text += f"Nights: {result.get('Nights', 'N/A')}\n"
            
            if 'BookingStatus' in result:
                status = result['BookingStatus']
                response_text += f"Status: {status.get('status', 'N/A')}\n"
            
            return CallToolResult(
                content=[TextContent(type="text", text=response_text)]
            )
        else:
            return CallToolResult(
                content=[TextContent(type="text", text="Booking failed. Please try again.")]
            )
    
    async def _get_hotel_info(self, arguments: Dict[str, Any]) -> CallToolResult:
        """Get detailed hotel information."""
        hotel_id = arguments["hotelId"]
        supplier = arguments.get("supplier", self.settings.default_supplier)
        
        # Prepare request data (excluding hotelId and supplier)
        request_data = {k: v for k, v in arguments.items() if k not in ["hotelId", "supplier"]}
        
        # Make API request
        result = await self.http_client.make_request(
            "POST",
            f"/api/hotels/{supplier}/{hotel_id}",
            request_data,
            supplier
        )
        
        # Format response
        if result.get("success") and result.get("data"):
            hotel = result["data"]
            response_text = f"🏨 **{hotel.get('name', 'N/A')}**\n\n"
            response_text += f"Hotel ID: {hotel.get('id', 'N/A')}\n"
            response_text += f"Currency: {hotel.get('currency', 'N/A')}\n\n"
            
            if 'description' in hotel:
                description = hotel['description'][:500] + "..." if len(hotel['description']) > 500 else hotel['description']
                response_text += f"**Description:**\n{description}\n\n"
            
            if 'HotelFacilities' in hotel:
                facilities = hotel['HotelFacilities'].replace('<BR />', '\n• ')
                response_text += f"**Hotel Facilities:**\n• {facilities}\n\n"
            
            if 'RoomFacilities' in hotel:
                room_facilities = hotel['RoomFacilities'].replace('<BR />', '\n• ')
                response_text += f"**Room Facilities:**\n• {room_facilities}\n"
            
            return CallToolResult(
                content=[TextContent(type="text", text=response_text)]
            )
        else:
            return CallToolResult(
                content=[TextContent(type="text", text="Hotel information not found.")]
            )
    
    async def _get_booking_details(self, arguments: Dict[str, Any]) -> CallToolResult:
        """Get booking details."""
        booking_id = arguments["bookingId"]
        supplier = arguments.get("supplier", self.settings.default_supplier)
        
        # Make API request
        result = await self.http_client.make_request(
            "GET",
            f"/api/hotels/{supplier}/booking/{booking_id}",
            None,
            supplier
        )
        
        # Format response
        if result.get("success") and result.get("data"):
            booking = result["data"]
            response_text = "📋 **Booking Details**\n\n"
            response_text += f"Booking ID: {booking.get('bookingId', 'N/A')}\n"
            response_text += f"Reference: {booking.get('GoReference', 'N/A')}\n"
            response_text += f"Hotel: {booking.get('HotelName', 'N/A')}\n"
            response_text += f"Total Price: {booking.get('TotalPrice', 'N/A')} {booking.get('Currency', 'N/A')}\n"
            response_text += f"Arrival Date: {booking.get('ArrivalDate', 'N/A')}\n"
            response_text += f"Nights: {booking.get('Nights', 'N/A')}\n"
            response_text += f"Created: {booking.get('CreatedDate', 'N/A')}\n"
            
            if 'BookingStatus' in booking:
                status = booking['BookingStatus']
                response_text += f"Status: {status.get('status', 'N/A')}\n"
                response_text += f"Description: {status.get('desc', 'N/A')}\n"
            
            if 'Leader' in booking:
                leader = booking['Leader']
                response_text += f"Lead Guest: {leader.get('value', 'N/A')}\n"
            
            return CallToolResult(
                content=[TextContent(type="text", text=response_text)]
            )
        else:
            return CallToolResult(
                content=[TextContent(type="text", text="Booking details not found.")]
            )
    
    async def _list_suppliers(self, arguments: Dict[str, Any]) -> CallToolResult:
        """List available suppliers."""
        # Make API request
        result = await self.http_client.make_request(
            "GET",
            "/api/hotels/suppliers",
            None
        )
        
        
        # Format response
        if result.get("success") and result.get("data"):
            suppliers = result["data"]
            response_text = "🏢 **Available Hotel Suppliers:**\n\n"
            
            for name, code in suppliers.items():
                response_text += f"• **{name}**: `{code}`\n"
            
            return CallToolResult(
                content=[TextContent(type="text", text=response_text)]
            )
        else:
            return CallToolResult(
                content=[TextContent(type="text", text="No suppliers found.")]
            )

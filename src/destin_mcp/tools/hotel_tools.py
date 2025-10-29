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
                title="Hotel Search Engine",
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
                },
                outputSchema={"type": "object"},
                annotations={
                    "title": "Hotel Search Engine",
                    "readOnlyHint": False,
                    "destructiveHint": False,
                    "idempotentHint": True,
                    "openWorldHint": False
                },
                icons=[]
            ),
            Tool(
                name="book_hotel",
                title="Hotel Booking System",
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
                },
                outputSchema={"type": "object"},
                annotations={
                    "title": "Hotel Booking System",
                    "readOnlyHint": False,
                    "destructiveHint": True,
                    "idempotentHint": False,
                    "openWorldHint": False
                },
                icons=[]
            ),
            Tool(
                name="get_hotel_info",
                title="Hotel Information Center",
                description="""ℹ️ **COMPREHENSIVE HOTEL INFORMATION CENTER**

**IMPORTANT FOR AI ASSISTANTS**: This tool provides complete hotel information in a conversational, helpful format!

**What it provides**:
- **Complete hotel profile** with star rating, location, contact details
- **Full property description** with amenities and features
- **Detailed facilities** (restaurants, pools, spa, gym, business center, etc.)
- **Room amenities** and in-room features
- **Hotel policies** including check-in/out times, age restrictions, pet policies
- **Available room types summary** with price ranges
- **Interactive guidance** on next steps (detailed rooms, booking process)

**Perfect for**:
- Getting comprehensive hotel information before booking
- Understanding all hotel amenities and services
- Learning about hotel policies and restrictions
- Seeing available room types and price ranges
- Getting guidance on the booking process

**Interactive Booking Flow**:
- Shows ALL available room options with full booking details
- Displays prices, fees, cancellation policies, and booking codes
- Numbers each room option for easy selection
- Guides users to choose specific rooms for booking
- Provides clear next steps: "I want to book Option 1"

**Returns**: Complete hotel information with numbered room options ready for immediate booking selection.""",
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
                },
                outputSchema={"type": "object"},
                annotations={
                    "title": "Hotel Information Center",
                    "readOnlyHint": True,
                    "destructiveHint": False,
                    "idempotentHint": True,
                    "openWorldHint": False
                },
                icons=[]
            ),
            Tool(
                name="get_booking_details",
                title="Booking Management System",
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
                },
                outputSchema={"type": "object"},
                annotations={
                    "title": "Booking Management System",
                    "readOnlyHint": True,
                    "destructiveHint": False,
                    "idempotentHint": True,
                    "openWorldHint": False
                },
                icons=[]
            ),
            Tool(
                name="list_suppliers",
                title="Supplier Network Directory",
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
                },
                outputSchema={"type": "object"},
                annotations={
                    "title": "Supplier Network Directory",
                    "readOnlyHint": True,
                    "destructiveHint": False,
                    "idempotentHint": True,
                    "openWorldHint": False
                },
                icons=[]
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
            # Log the actual response structure for debugging
            logger.debug(f"Booking API response: {result}")
            
            # Check if the response indicates success
            if result.get("success") and result.get("data"):
                booking_data = result["data"]
                response_text = "🎉 **Hotel Booking Confirmation**\n\n"
                response_text += f"Booking ID: {booking_data.get('GoBookingCode', booking_data.get('bookingId', booking_data.get('id', 'N/A')))}\n"
                response_text += f"Reference: {booking_data.get('GoReference', booking_data.get('reference', booking_data.get('confirmationNumber', 'N/A')))}\n"
                response_text += f"Hotel: {booking_data.get('HotelName', booking_data.get('hotelName', booking_data.get('name', 'N/A')))}\n"
                response_text += f"Total Price: {booking_data.get('TotalPrice', booking_data.get('totalPrice', booking_data.get('price', 'N/A')))} {booking_data.get('Currency', booking_data.get('currency', 'N/A'))}\n"
                response_text += f"Arrival Date: {booking_data.get('ArrivalDate', booking_data.get('checkIn', booking_data.get('fromDate', 'N/A')))}\n"
                response_text += f"Nights: {booking_data.get('Nights', booking_data.get('nights', 'N/A'))}\n"
                
                if 'BookingStatus' in booking_data:
                    status = booking_data['BookingStatus']
                    response_text += f"Status: {status.get('status', 'N/A')}\n"
                elif 'status' in booking_data:
                    response_text += f"Status: {booking_data['status']}\n"
                
                return CallToolResult(
                    content=[TextContent(type="text", text=response_text)]
                )
            else:
                # Handle error responses or unexpected structure
                error_msg = "Booking failed."
                if isinstance(result, dict):
                    if "message" in result:
                        error_msg += f" Error: {result['message']}"
                    elif "error" in result:
                        error_msg += f" Error: {result['error']}"
                    elif "Message" in result:
                        error_msg += f" Error: {result['Message']}"
                    else:
                        # Show the actual response structure for debugging
                        response_text = f"🔍 **Debug Information**\n\n"
                        response_text += f"API Response Structure:\n```json\n{result}\n```\n\n"
                        response_text += "The booking API returned an unexpected response format. "
                        response_text += "Please check the API documentation or contact support."
                        
                        return CallToolResult(
                            content=[TextContent(type="text", text=response_text)]
                        )
                
                return CallToolResult(
                    content=[TextContent(type="text", text=error_msg)]
                )
        else:
            return CallToolResult(
                content=[TextContent(type="text", text="Booking failed. No response from API.")]
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
            
            # Basic hotel information
            response_text += f"📍 **Hotel Details:**\n"
            response_text += f"• Hotel ID: {hotel.get('id', 'N/A')}\n"
            response_text += f"• Star Rating: {hotel.get('starRating', 'N/A')} stars\n"
            response_text += f"• Currency: {hotel.get('currency', 'N/A')}\n"
            
            # Location information
            if 'location' in hotel:
                location = hotel['location']
                response_text += f"• Address: {location.get('address', 'N/A')}\n"
                response_text += f"• City: {location.get('destination', 'N/A')}\n"
                response_text += f"• Country: {location.get('country', 'N/A')}\n"
            
            if hotel.get('telephone'):
                response_text += f"• Phone: {hotel['telephone']}\n"
            
            response_text += "\n"
            
            # Hotel description
            if 'description' in hotel:
                # Clean up HTML tags and show full description
                description = hotel['description'].replace('<p>', '').replace('</p>', '\n').replace('<b>', '**').replace('</b>', '**').replace('<br/>', '\n')
                response_text += f"📝 **Hotel Description:**\n{description}\n\n"
            
            # Hotel facilities
            if 'HotelFacilities' in hotel:
                facilities = hotel['HotelFacilities'].replace('<BR />', '\n• ')
                response_text += f"🏢 **Hotel Facilities:**\n• {facilities}\n\n"
            
            # Room facilities
            if 'RoomFacilities' in hotel:
                room_facilities = hotel['RoomFacilities'].replace('<BR />', '\n• ')
                response_text += f"🛏️ **Room Amenities:**\n• {room_facilities}\n\n"
            
            # Check-in/out policies
            if 'policy' in hotel and hotel['policy']:
                policy = hotel['policy']
                response_text += f"📋 **Hotel Policies:**\n"
                if policy.get('checkinFrom'):
                    response_text += f"• Check-in: {policy['checkinFrom']}\n"
                if policy.get('checkoutTo'):
                    response_text += f"• Check-out: {policy['checkoutTo']}\n"
                
                # Extra info
                if 'extraInfoList' in policy:
                    for info in policy['extraInfoList']:
                        if info.get('description') and info.get('value'):
                            response_text += f"• {info['description']}: {info['value']}\n"
                        elif info.get('description'):
                            response_text += f"• {info['description']}\n"
                response_text += "\n"
            
            # Available rooms summary
            if 'rooms' in hotel and hotel['rooms']:
                # Group rooms by type
                room_types = {}
                for room in hotel['rooms']:
                    room_names = room.get('Rooms', [])
                    if room_names:
                        for room_name in room_names:
                            if room_name not in room_types:
                                room_types[room_name] = []
                            room_types[room_name].append({
                                'price': room.get('TotalPrice', 0),
                                'currency': room.get('Currency', 'USD'),
                                'room_basis': room.get('RoomBasis', ''),
                                'room_code': room.get('HotelSearchCode', ''),
                                'cancellation': room.get('CxlDeadLine', ''),
                                'fees': room.get('Fee', [])
                            })
                
                response_text += f"🛏️ **Available Room Options for Booking ({len(hotel['rooms'])} total options):**\n\n"
                
                # Show ALL room options with full details for booking
                room_counter = 1
                for room in hotel['rooms']:
                    room_names = room.get('Rooms', [])
                    if room_names:
                        for room_name in room_names:
                            response_text += f"**Option {room_counter}: {room_name}**\n"
                            response_text += f"• Price: {room.get('TotalPrice', 'N/A')} {room.get('Currency', 'USD')}\n"
                            
                            # Show fees if available
                            if room.get('Fee'):
                                for fee in room['Fee']:
                                    fee_name = fee.get('FeeTypeName', fee.get('Type', 'Additional Fee'))
                                    response_text += f"• {fee_name}: {fee.get('Amount', 'N/A')} {fee.get('Currency', 'USD')}\n"
                            
                            response_text += f"• Room Basis: {room.get('RoomBasis', 'Not specified')}\n"
                            response_text += f"• Booking Code: `{room.get('HotelSearchCode', 'N/A')}`\n"
                            
                            if room.get('CxlDeadLine'):
                                response_text += f"• Cancellation Deadline: {room['CxlDeadLine']}\n"
                            
                            if room.get('CancellationPolicies'):
                                for policy in room['CancellationPolicies']:
                                    if policy.get('FromDate') and policy.get('Amount'):
                                        response_text += f"• Cancellation Fee: {policy['Amount']} {room.get('Currency', 'USD')} from {policy['FromDate']}\n"
                            
                            response_text += "\n"
                            room_counter += 1
                
                response_text += "🎯 **NEXT STEP: Choose Your Room!**\n"
                response_text += "To book, tell me: *'I want to book Option [number]'* or *'Book room with code [booking code]'*\n"
                response_text += "Example: *'I want to book Option 1'* or *'Book the Executive Room for $664'*\n\n"
            
            # Booking suggestion
            response_text += "🎯 **Ready to book?**\n"
            response_text += "Use the `book_hotel` tool with:\n"
            response_text += f"• Hotel ID: `{hotel.get('id')}`\n"
            response_text += "• Choose a room code from the available options\n"
            response_text += "• Provide guest details and contact information\n\n"
            
            response_text += "📞 **Need more help?** Ask me about:\n"
            response_text += "• Detailed room options and pricing\n"
            response_text += "• Booking process and requirements\n"
            response_text += "• Hotel amenities and services\n"
            response_text += "• Cancellation policies\n"
            
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

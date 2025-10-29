"""Hotel-related MCP tools."""

from typing import Any, Dict, List
from datetime import datetime

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
    
    def _calculate_nights(self, from_date: str, to_date: str) -> int:
        """Calculate number of nights between dates."""
        try:
            check_in = datetime.strptime(from_date, "%Y-%m-%d")
            check_out = datetime.strptime(to_date, "%Y-%m-%d")
            return (check_out - check_in).days
        except:
            return 1
    
    def _format_price_breakdown(self, room_data: Dict, occupancy: List[Dict], nights: int) -> str:
        """Format detailed price breakdown with per-night and per-guest calculations."""
        total_price = room_data.get('TotalPrice', room_data.get('price', 0))
        currency = room_data.get('Currency', room_data.get('currency', 'EUR'))
        
        # Calculate totals
        total_adults = sum(occ.get('adults', 1) for occ in occupancy)
        total_rooms = sum(occ.get('roomCount', 1) for occ in occupancy)
        
        # Base calculations
        price_per_night = total_price / nights if nights > 0 else total_price
        price_per_room_per_night = price_per_night / total_rooms if total_rooms > 0 else price_per_night
        price_per_person_total = total_price / total_adults if total_adults > 0 else total_price
        
        breakdown = f"💰 **Price Breakdown:**\n"
        breakdown += f"• **Total Price**: {total_price:.2f} {currency}\n"
        breakdown += f"• **Per Night**: {price_per_night:.2f} {currency} ({nights} night{'s' if nights != 1 else ''})\n"
        breakdown += f"• **Per Room/Night**: {price_per_room_per_night:.2f} {currency} ({total_rooms} room{'s' if total_rooms != 1 else ''})\n"
        breakdown += f"• **Per Person (Total)**: {price_per_person_total:.2f} {currency} ({total_adults} guest{'s' if total_adults != 1 else ''})\n"
        
        # Add fee breakdown if available
        if room_data.get('Fee'):
            breakdown += f"\n📋 **Additional Fees:**\n"
            total_fees = 0
            for fee in room_data['Fee']:
                fee_amount = fee.get('Amount', 0)
                fee_currency = fee.get('Currency', currency)
                fee_name = fee.get('FeeTypeName', fee.get('Type', 'Additional Fee'))
                breakdown += f"• {fee_name}: {fee_amount} {fee_currency}\n"
                if fee_currency == currency:
                    total_fees += fee_amount
            
            if total_fees > 0:
                grand_total = total_price + total_fees
                breakdown += f"• **Total with Fees**: {grand_total:.2f} {currency}\n"
        
        return breakdown
    
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
   - Use defaults: currency=EUR, supplier=dida

**Purpose**: Search and discover available hotels with comprehensive pricing analysis and availability.

**What it does**:
- Searches thousands of hotels across global destinations
- Provides **detailed pricing breakdown** in EUR (default) or specified currency
- Shows **per-night calculations** and **per-guest pricing**
- Returns **enhanced price analysis** including:
  * Total stay cost with currency
  * Price per night breakdown
  * Cost per guest for the entire stay
  * Visual formatting with separators and numbering
- Shows room availability for specific dates and guest configurations
- Returns detailed hotel information including amenities and location
- Supports multiple room types and guest combinations

**Enhanced Pricing Display Features**:
- **Numbered hotel listings** for easy reference
- **Per-night cost calculations** based on stay duration
- **Per-guest pricing** based on total occupancy
- **Professional formatting** with icons and visual separators
- **Room basis and booking codes** clearly displayed

**City Code Reference**:
- Mumbai/Bombay → BOM
- Delhi/New Delhi → DEL  
- Bangalore/Bengaluru → BLR
- Chennai/Madras → MAA
- Kolkata/Calcutta → CCU

**Returns**: Numbered list of hotels with comprehensive pricing analysis, per-night/per-guest calculations, room details, supplier info, and booking codes in a professional, easy-to-read format.""",
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
                            "description": "Currency code (default: EUR)",
                            "default": "EUR"
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

**IMPORTANT FOR AI ASSISTANTS**: Always include the hotelId from search results when booking! Present booking confirmations in a professional, detailed format.

**Purpose**: Complete hotel reservation system with instant booking confirmation, detailed pricing breakdown, and guest management.

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
- Provides **comprehensive booking confirmation** with enhanced pricing display

**Enhanced Booking Confirmation Features**:
- **Professional booking confirmation** with structured sections
- **Detailed payment summary** including:
  * Total amount in EUR (or specified currency)
  * Per-night breakdown for multi-night stays
  * Clear pricing calculations
- **Organized information display** with:
  * Booking Information section (ID, Reference, Hotel)
  * Payment Summary section (Total, Per-night calculations)
  * Stay Details section (Check-in, Duration)
- **Status tracking** and confirmation details

**Key Features**:
- Instant booking confirmation with reference numbers
- Support for multiple guests per room with individual details
- **Enhanced price breakdown** including base rate, taxes, and fees with per-night calculations
- Real-time inventory management and room allocation
- Booking status tracking and management
- Cancellation policy information

**Use cases**:
- Book corporate accommodations for business travelers
- Reserve family rooms with multiple guest configurations
- Create group bookings for events or conferences
- Secure last-minute hotel reservations
- Book accommodations with specific guest requirements

**Returns**: Professional booking confirmation with structured sections including booking ID, reference number, detailed payment summary with per-night calculations, hotel details, and guest information in EUR currency.""",
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
                            "description": "Currency code (default: EUR)",
                            "default": "EUR"
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

**IMPORTANT FOR AI ASSISTANTS**: This tool provides complete hotel information with **advanced pricing analysis** in a conversational, professional format!

**What it provides**:
- **Complete hotel profile** with star rating, location, contact details
- **Full property description** with amenities and features
- **Detailed facilities** (restaurants, pools, spa, gym, business center, etc.)
- **Room amenities** and in-room features
- **Hotel policies** including check-in/out times, age restrictions, pet policies
- **Comprehensive room pricing analysis** with detailed breakdowns
- **Interactive guidance** on next steps (detailed rooms, booking process)

**Advanced Pricing Features**:
- **Detailed price breakdown** for each room option including:
  * Total price in EUR (or specified currency)
  * Per-night calculations based on stay duration
  * Per-room/per-night breakdown for multiple rooms
  * Per-person total cost based on occupancy
- **Additional fees itemization** with separate currency handling
- **Tax and fee totals** when applicable
- **Professional formatting** with visual separators and structured sections

**Perfect for**:
- Getting comprehensive hotel information with detailed pricing analysis
- Understanding all hotel amenities and services with cost breakdowns
- Learning about hotel policies and restrictions
- **Comparing room options** with complete price analysis
- Getting guidance on the booking process with clear pricing

**Interactive Booking Flow**:
- Shows **ALL available room options** with comprehensive pricing details
- **Numbers each room option** for easy selection and reference
- Displays **detailed price breakdowns**, fees, cancellation policies, and booking codes
- **Professional formatting** with structured sections and visual separators
- Guides users to choose specific rooms for booking with clear pricing information
- Provides clear next steps: "I want to book Option 1"

**Enhanced Display Features**:
- **Structured room information** with price breakdown sections
- **Visual separators** between room options for clarity
- **Comprehensive fee analysis** including cancellation policies
- **Professional formatting** with icons and clear sections

**Returns**: Complete hotel information with numbered, professionally formatted room options including comprehensive pricing analysis, detailed breakdowns, fee itemization, and booking guidance in EUR currency.""",
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

**IMPORTANT FOR AI ASSISTANTS**: Present booking details in a professional, structured format with enhanced pricing analysis!
                
**Purpose**: Complete booking information retrieval and management system for existing hotel reservations with detailed pricing breakdown.

**What it does**:
- Retrieves comprehensive booking details and current status
- Provides real-time booking status updates and confirmations
- Shows complete guest information and room assignments
- **Displays enhanced pricing breakdown** with per-night calculations
- Offers cancellation and modification policy information
- Tracks booking history and status changes

**Enhanced Pricing Display Features**:
- **Professional payment summary** including:
  * Total amount in EUR (or booking currency)
  * Per-night breakdown for multi-night stays
  * Clear pricing calculations and currency display
- **Structured information sections** for better readability
- **Comprehensive booking analysis** with all financial details

**Comprehensive Details Include**:
- Booking confirmation number and reference codes
- Current booking status (confirmed, cancelled, modified, etc.)
- Complete guest information and room assignments
- Hotel details, location, and contact information
- Check-in/check-out dates and special instructions
- **Enhanced pricing breakdown** with per-night calculations in EUR
- **Professional payment summary** with structured display
- Cancellation policies and modification options
- Special requests and preferences
- Booking creation and modification history

**Use cases**:
- Verify booking details with comprehensive pricing analysis before travel
- Check booking status and confirmations with financial breakdown
- Review cancellation and modification policies
- Access guest information for check-in purposes
- Resolve booking issues and discrepancies with pricing details
- Manage corporate travel booking records with detailed cost analysis
- Provide booking information to travel companions with clear pricing

**Returns**: Complete booking record with professional formatting, enhanced pricing breakdown including per-night calculations, status information, guest details, and policy information in EUR currency.""",
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
                nights = self._calculate_nights(search_data.fromDate, search_data.toDate)
                response_text = f"🏨 **Found {len(hotels)} hotels** ({nights} night{'s' if nights != 1 else ''})\n\n"
                
                for i, hotel in enumerate(hotels, 1):
                    response_text += f"**{i}. {hotel.get('name', 'N/A')}**\n"
                    response_text += f"📍 Hotel ID: `{hotel.get('id', 'N/A')}`\n"
                    response_text += f"🏢 Supplier: {hotel.get('supplier', 'N/A')}\n"
                    
                    if 'rooms' in hotel:
                        room = hotel['rooms']
                        total_price = room.get('price', 0)
                        currency = room.get('currency', 'EUR')
                        
                        # Enhanced price display
                        response_text += f"\n💰 **Pricing:**\n"
                        response_text += f"• **Total**: {total_price} {currency}\n"
                        
                        if nights > 0:
                            price_per_night = total_price / nights
                            response_text += f"• **Per Night**: {price_per_night:.2f} {currency}\n"
                        
                        # Calculate per guest if occupancy available
                        if hasattr(search_data, 'occupancy') and search_data.occupancy:
                            total_guests = sum(occ.get('adults', 1) for occ in search_data.occupancy)
                            if total_guests > 0:
                                price_per_guest = total_price / total_guests
                                response_text += f"• **Per Guest**: {price_per_guest:.2f} {currency} (total for {total_guests} guest{'s' if total_guests != 1 else ''})\n"
                        
                        response_text += f"• **Room Basis**: {room.get('room_basis', 'Not specified')}\n"
                        response_text += f"• **Room Code**: `{room.get('id', 'N/A')}`\n"
                    
                    response_text += "\n" + "─" * 50 + "\n\n"
                
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
                
                # Booking details
                response_text += f"📋 **Booking Information:**\n"
                response_text += f"• **Booking ID**: {booking_data.get('GoBookingCode', booking_data.get('bookingId', booking_data.get('id', 'N/A')))}\n"
                response_text += f"• **Reference**: {booking_data.get('GoReference', booking_data.get('reference', booking_data.get('confirmationNumber', 'N/A')))}\n"
                response_text += f"• **Hotel**: {booking_data.get('HotelName', booking_data.get('hotelName', booking_data.get('name', 'N/A')))}\n"
                
                # Enhanced pricing display
                total_price = booking_data.get('TotalPrice', booking_data.get('totalPrice', booking_data.get('price', 0)))
                currency = booking_data.get('Currency', booking_data.get('currency', 'EUR'))
                nights = booking_data.get('Nights', booking_data.get('nights', 1))
                
                response_text += f"\n💰 **Payment Summary:**\n"
                response_text += f"• **Total Amount**: {total_price} {currency}\n"
                
                if nights and nights > 0:
                    price_per_night = total_price / nights if isinstance(total_price, (int, float)) else 0
                    response_text += f"• **Per Night**: {price_per_night:.2f} {currency} × {nights} night{'s' if nights != 1 else ''}\n"
                
                response_text += f"\n📅 **Stay Details:**\n"
                response_text += f"• **Check-in**: {booking_data.get('ArrivalDate', booking_data.get('checkIn', booking_data.get('fromDate', 'N/A')))}\n"
                response_text += f"• **Duration**: {nights} night{'s' if nights != 1 else ''}\n"
                
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
                                'currency': room.get('Currency', 'EUR'),
                                'room_basis': room.get('RoomBasis', ''),
                                'room_code': room.get('HotelSearchCode', ''),
                                'cancellation': room.get('CxlDeadLine', ''),
                                'fees': room.get('Fee', [])
                            })
                
                response_text += f"🛏️ **Available Room Options for Booking ({len(hotel['rooms'])} total options):**\n\n"
                
                # Show ALL room options with full details for booking
                room_counter = 1
                nights = self._calculate_nights(arguments['fromDate'], arguments['toDate'])
                occupancy = arguments.get('occupancy', [{'adults': 1, 'roomCount': 1}])
                
                for room in hotel['rooms']:
                    room_names = room.get('Rooms', [])
                    if room_names:
                        for room_name in room_names:
                            response_text += f"**Option {room_counter}: {room_name}**\n"
                            
                            # Enhanced price breakdown using helper method
                            price_breakdown = self._format_price_breakdown(room, occupancy, nights)
                            response_text += price_breakdown + "\n"
                            
                            response_text += f"🛏️ **Room Details:**\n"
                            response_text += f"• **Room Basis**: {room.get('RoomBasis', 'Not specified')}\n"
                            response_text += f"• **Booking Code**: `{room.get('HotelSearchCode', 'N/A')}`\n"
                            
                            if room.get('CxlDeadLine'):
                                response_text += f"• **Cancellation Deadline**: {room['CxlDeadLine']}\n"
                            
                            if room.get('CancellationPolicies'):
                                response_text += f"• **Cancellation Policy**:\n"
                                for policy in room['CancellationPolicies']:
                                    if policy.get('FromDate') and policy.get('Amount'):
                                        response_text += f"  - Fee: {policy['Amount']} {room.get('Currency', 'EUR')} from {policy['FromDate']}\n"
                            
                            response_text += "\n" + "─" * 40 + "\n\n"
                            room_counter += 1
                
                response_text += "🎯 **NEXT STEP: Choose Your Room!**\n"
                response_text += "To book, tell me: *'I want to book Option [number]'* or *'Book room with code [booking code]'*\n"
                response_text += "Example: *'I want to book Option 1'* or *'Book the Executive Room'*\n\n"
            
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
            # Enhanced pricing display for booking details
            total_price = booking.get('TotalPrice', 0)
            currency = booking.get('Currency', 'EUR')
            nights = booking.get('Nights', 1)
            
            response_text += f"\n💰 **Payment Summary:**\n"
            response_text += f"• **Total Amount**: {total_price} {currency}\n"
            
            if nights and nights > 0 and isinstance(total_price, (int, float)):
                price_per_night = total_price / nights
                response_text += f"• **Per Night**: {price_per_night:.2f} {currency} × {nights} night{'s' if nights != 1 else ''}\n"
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

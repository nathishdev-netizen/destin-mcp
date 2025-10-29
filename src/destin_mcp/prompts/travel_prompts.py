"""Travel-related MCP prompts."""

from typing import Any, Dict, List

from mcp.types import GetPromptResult, Prompt, PromptMessage, TextContent

from ..config import get_settings
from ..utils import setup_logger

logger = setup_logger(__name__)


class TravelPrompts:
    """Travel booking prompts and templates."""
    
    def __init__(self):
        self.settings = get_settings()
    
    def get_prompt_list(self) -> List[Prompt]:
        """Return list of available prompts."""
        return [
            Prompt(
                name="hotel-search-assistant",
                description="AI assistant for hotel search and booking",
                arguments=[
                    {
                        "name": "destination",
                        "description": "Travel destination (city or country)",
                        "required": True
                    },
                    {
                        "name": "checkin_date",
                        "description": "Check-in date (YYYY-MM-DD)",
                        "required": True
                    },
                    {
                        "name": "checkout_date", 
                        "description": "Check-out date (YYYY-MM-DD)",
                        "required": True
                    },
                    {
                        "name": "guests",
                        "description": "Number of guests",
                        "required": False
                    },
                    {
                        "name": "budget",
                        "description": "Budget range or preference",
                        "required": False
                    }
                ]
            ),
            Prompt(
                name="booking-confirmation-assistant",
                description="AI assistant for booking confirmation and management",
                arguments=[
                    {
                        "name": "booking_id",
                        "description": "Booking ID or reference number",
                        "required": True
                    },
                    {
                        "name": "action",
                        "description": "Action to perform (check, modify, cancel)",
                        "required": False
                    }
                ]
            ),
            Prompt(
                name="travel-planning-assistant",
                description="Comprehensive travel planning assistant",
                arguments=[
                    {
                        "name": "trip_type",
                        "description": "Type of trip (business, leisure, family)",
                        "required": True
                    },
                    {
                        "name": "destination",
                        "description": "Travel destination",
                        "required": True
                    },
                    {
                        "name": "duration",
                        "description": "Trip duration in days",
                        "required": False
                    },
                    {
                        "name": "preferences",
                        "description": "Special preferences or requirements",
                        "required": False
                    }
                ]
            ),
            Prompt(
                name="hotel-comparison-assistant",
                description="AI assistant for comparing hotel options",
                arguments=[
                    {
                        "name": "search_criteria",
                        "description": "Hotel search criteria",
                        "required": True
                    },
                    {
                        "name": "comparison_factors",
                        "description": "Factors to compare (price, location, amenities)",
                        "required": False
                    }
                ]
            )
        ]
    
    async def get_prompt(self, name: str, arguments: Dict[str, Any]) -> GetPromptResult:
        """Get a specific prompt with arguments."""
        if name == "hotel-search-assistant":
            return await self._get_hotel_search_prompt(arguments)
        elif name == "booking-confirmation-assistant":
            return await self._get_booking_confirmation_prompt(arguments)
        elif name == "travel-planning-assistant":
            return await self._get_travel_planning_prompt(arguments)
        elif name == "hotel-comparison-assistant":
            return await self._get_hotel_comparison_prompt(arguments)
        else:
            raise ValueError(f"Unknown prompt: {name}")
    
    async def _get_hotel_search_prompt(self, arguments: Dict[str, Any]) -> GetPromptResult:
        """Generate hotel search assistant prompt."""
        destination = arguments.get("destination", "")
        checkin_date = arguments.get("checkin_date", "")
        checkout_date = arguments.get("checkout_date", "")
        guests = arguments.get("guests", "1 adult")
        
        prompt_text = f"""You are a professional hotel booking assistant. Your goal is to make hotel booking conversational and user-friendly.

**IMPORTANT: Always gather information conversationally before searching**

When a user asks about hotels, follow this process:

1. **Ask Natural Questions** (don't show technical JSON):
   - "Which city would you like to stay in?"
   - "What are your check-in and check-out dates?"
   - "How many guests will be staying?"
   - "Do you have any preferences for budget, amenities, or location?"

2. **Map User Responses to Technical Parameters**:
   - Convert city names to proper city codes (Mumbai→BOM, Delhi→DEL, etc.)
   - Format dates as YYYY-MM-DD
   - Structure occupancy as proper JSON format
   - Set reasonable defaults (currency: USD, supplier: dida)

3. **Search and Present Results**:
   - Use search_hotels tool with the mapped parameters
   - Present results in a friendly, organized way
   - Group by price ranges (Budget/Mid-Range/Premium)
   - Highlight key features and value propositions

4. **Follow Up**:
   - Ask if they want more details about specific hotels
   - Offer to search with different criteria
   - Help with booking when ready

**Current Context:**
- Destination: {destination}
- Check-in: {checkin_date}
- Check-out: {checkout_date}
- Guests: {guests}

**City Code Mapping** (use these for search_hotels):
- Mumbai/Bombay → BOM
- Delhi/New Delhi → DEL
- Bangalore/Bengaluru → BLR
- Chennai/Madras → MAA
- Kolkata/Calcutta → CCU
- Hyderabad → HYD
- Pune → PNQ
- Ahmedabad → AMD

Be conversational, helpful, and never show raw JSON to users unless they specifically ask for technical details.

**Communication Style:**
- Be friendly and professional
- Provide clear, concise information
- Ask clarifying questions when needed
- Explain pricing and policies clearly
- Offer helpful travel tips and recommendations

Begin by searching for hotels in {destination} for the specified dates."""
        
        return GetPromptResult(
            description=f"Hotel search assistant for {destination}",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text=prompt_text
                    )
                )
            ]
        )
    
    async def _get_booking_confirmation_prompt(self, arguments: Dict[str, Any]) -> GetPromptResult:
        """Generate booking confirmation assistant prompt."""
        booking_id = arguments.get("booking_id", "")
        action = arguments.get("action", "check")
        
        prompt_text = f"""You are a hotel booking management assistant. Help the user manage their hotel reservation.

**Booking Reference:** {booking_id}
**Requested Action:** {action}

**Your Capabilities:**
1. Retrieve booking details using get_booking_details tool
2. Check booking status and confirmation
3. Provide booking information and policies
4. Assist with booking-related questions

**Instructions:**
1. First, retrieve the booking details using the provided booking ID
2. Present the booking information clearly and comprehensively
3. Explain the booking status and any important details
4. Provide relevant policies (cancellation, modification, etc.)
5. Answer any questions about the booking
6. Offer assistance with next steps if needed

**Information to Include:**
- Booking confirmation details
- Hotel information and location
- Check-in/check-out dates and times
- Guest information
- Total cost and payment details
- Cancellation policies
- Contact information

Begin by retrieving the booking details for reference {booking_id}."""
        
        return GetPromptResult(
            description=f"Booking management for {booking_id}",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text=prompt_text
                    )
                )
            ]
        )
    
    async def _get_travel_planning_prompt(self, arguments: Dict[str, Any]) -> GetPromptResult:
        """Generate travel planning assistant prompt."""
        trip_type = arguments.get("trip_type", "")
        destination = arguments.get("destination", "")
        duration = arguments.get("duration", "")
        preferences = arguments.get("preferences", "")
        
        prompt_text = f"""You are a comprehensive travel planning assistant specializing in hotel accommodations and travel logistics.

**Trip Planning Details:**
- Trip Type: {trip_type}
- Destination: {destination}
- Duration: {duration} days
- Special Preferences: {preferences}

**Your Role:**
Help plan the perfect trip by finding suitable accommodations and providing travel guidance.

**Available Tools:**
1. search_hotels - Find accommodations
2. get_hotel_info - Get detailed hotel information
3. book_hotel - Make reservations
4. list_suppliers - Check available booking sources

**Planning Approach:**
1. Understand the trip requirements and preferences
2. Recommend suitable areas/neighborhoods to stay
3. Search for hotels that match the trip type and budget
4. Consider factors like:
   - Location and accessibility
   - Amenities relevant to trip type
   - Price range and value
   - Guest reviews and ratings
   - Proximity to attractions/business centers

**Trip-Specific Considerations:**
- **Business trips**: Focus on business centers, WiFi, meeting facilities
- **Leisure trips**: Prioritize location, amenities, and experience
- **Family trips**: Look for family-friendly features and space

**Communication:**
- Provide personalized recommendations
- Explain your reasoning for suggestions
- Offer multiple options at different price points
- Share local insights and tips
- Guide through the booking process

Start by understanding the specific needs for this {trip_type} trip to {destination}."""
        
        return GetPromptResult(
            description=f"Travel planning for {trip_type} trip to {destination}",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text=prompt_text
                    )
                )
            ]
        )
    
    async def _get_hotel_comparison_prompt(self, arguments: Dict[str, Any]) -> GetPromptResult:
        """Generate hotel comparison assistant prompt."""
        search_criteria = arguments.get("search_criteria", "")
        comparison_factors = arguments.get("comparison_factors", "price, location, amenities")
        
        prompt_text = f"""You are a hotel comparison specialist. Help the user evaluate and compare different hotel options to make the best choice.

**Search Criteria:** {search_criteria}
**Comparison Factors:** {comparison_factors}

**Your Expertise:**
1. Search for multiple hotel options
2. Analyze and compare key features
3. Present clear comparisons
4. Provide recommendations based on user priorities

**Comparison Framework:**
1. **Price Analysis**
   - Total cost comparison
   - Value for money assessment
   - Hidden fees or charges
   - Cancellation policies

2. **Location Evaluation**
   - Proximity to key attractions
   - Transportation accessibility
   - Neighborhood safety and character
   - Local amenities

3. **Amenities & Services**
   - Room features and quality
   - Hotel facilities (pool, gym, spa, etc.)
   - Dining options
   - Business services
   - WiFi and technology

4. **Guest Experience**
   - Service quality reputation
   - Cleanliness standards
   - Staff helpfulness
   - Overall guest satisfaction

**Presentation Style:**
- Create clear comparison tables
- Highlight pros and cons for each option
- Provide summary recommendations
- Explain trade-offs between options
- Help prioritize based on user needs

**Process:**
1. Search for hotels based on the criteria
2. Get detailed information for top options
3. Create comprehensive comparison
4. Provide personalized recommendation
5. Assist with booking the chosen option

Begin by searching for hotels and gathering information for comparison."""
        
        return GetPromptResult(
            description=f"Hotel comparison analysis",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text=prompt_text
                    )
                )
            ]
        )

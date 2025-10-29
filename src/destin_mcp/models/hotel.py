"""Hotel-related data models."""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, validator


class OccupancyModel(BaseModel):
    """Room occupancy model."""
    
    adults: int = Field(
        ge=1, 
        le=10, 
        description="Number of adults (1-10)"
    )
    roomCount: int = Field(
        ge=1, 
        le=5, 
        description="Number of rooms (1-5)"
    )
    childAges: Optional[List[int]] = Field(
        default=None, 
        description="Ages of children"
    )


class ContactNameModel(BaseModel):
    """Contact name model."""
    
    First: str = Field(
        description="Contact first name"
    )
    Last: str = Field(
        description="Contact last name"
    )


class ContactModel(BaseModel):
    """Contact information model for booking."""
    
    Name: ContactNameModel = Field(
        description="Contact name details"
    )
    Email: str = Field(
        description="Contact email address"
    )
    Phone: str = Field(
        description="Contact phone number"
    )


class GuestModel(BaseModel):
    """Guest information model."""
    
    title: str = Field(
        description="Guest title (MR., MRS., MS., etc.)"
    )
    firstName: str = Field(
        min_length=1, 
        max_length=50, 
        description="Guest first name"
    )
    lastName: str = Field(
        min_length=1, 
        max_length=50, 
        description="Guest last name"
    )


class RoomModel(BaseModel):
    """Room booking model."""
    
    adults: int = Field(
        ge=1, 
        le=10, 
        description="Number of adults in room"
    )
    guests: List[GuestModel] = Field(
        description="Guest details for the room"
    )


class HotelSearchModel(BaseModel):
    """Hotel search request model."""
    
    country: str = Field(
        min_length=2, 
        max_length=2, 
        description="Country code (e.g., 'IN')"
    )
    fromDate: str = Field(
        description="Check-in date (YYYY-MM-DD)"
    )
    toDate: str = Field(
        description="Check-out date (YYYY-MM-DD)"
    )
    cityCode: Optional[str] = Field(
        default=None, 
        description="City code"
    )
    sort: Optional[int] = Field(
        default=1, 
        description="Sort order"
    )
    currency: Optional[str] = Field(
        default="USD", 
        description="Currency code"
    )
    occupancy: List[OccupancyModel] = Field(
        description="Room occupancy details"
    )

    @validator('fromDate', 'toDate')
    def validate_date_format(cls, v):
        """Validate date format."""
        try:
            datetime.strptime(v, '%Y-%m-%d')
            return v
        except ValueError:
            raise ValueError('Date must be in YYYY-MM-DD format')

    @validator('toDate')
    def validate_date_order(cls, v, values):
        """Validate that toDate is after fromDate."""
        if 'fromDate' in values:
            from_date = datetime.strptime(values['fromDate'], '%Y-%m-%d')
            to_date = datetime.strptime(v, '%Y-%m-%d')
            if to_date <= from_date:
                raise ValueError('Check-out date must be after check-in date')
        return v


class HotelBookingModel(BaseModel):
    """Hotel booking request model."""
    
    hotelId: str = Field(
        description="Hotel ID from search results"
    )
    country: str = Field(
        min_length=2, 
        max_length=2, 
        description="Country code"
    )
    currency: str = Field(
        default="USD", 
        description="Currency code"
    )
    fromDate: str = Field(
        description="Check-in date (YYYY-MM-DD)"
    )
    toDate: str = Field(
        description="Check-out date (YYYY-MM-DD)"
    )
    roomCode: str = Field(
        description="Room code from search results"
    )
    contact: ContactModel = Field(
        description="Primary contact information for booking"
    )
    rooms: List[RoomModel] = Field(
        description="Room and guest details"
    )

    @validator('fromDate', 'toDate')
    def validate_date_format(cls, v):
        """Validate date format."""
        try:
            datetime.strptime(v, '%Y-%m-%d')
            return v
        except ValueError:
            raise ValueError('Date must be in YYYY-MM-DD format')

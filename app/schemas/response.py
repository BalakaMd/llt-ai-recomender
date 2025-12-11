"""Response schemas for AI Recommender Service."""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class GeoCoordinates(BaseModel):
    """Geographic coordinates."""
    
    lat: float = Field(..., ge=-90, le=90, description="Latitude")
    lng: float = Field(..., ge=-180, le=180, description="Longitude")


class ItineraryItem(BaseModel):
    """Single activity/place in the itinerary."""
    
    day_index: int = Field(
        ...,
        ge=1,
        description="Day number (1-indexed)"
    )
    order_index: int = Field(
        ...,
        ge=1,
        description="Order within the day (1-indexed)"
    )
    title: str = Field(
        ...,
        min_length=2,
        max_length=200,
        description="Activity title"
    )
    description: str = Field(
        ...,
        min_length=10,
        max_length=1000,
        description="Detailed description of the activity"
    )
    place_name: str = Field(
        ...,
        min_length=2,
        max_length=200,
        description="Name of the place/venue"
    )
    coordinates: Optional[GeoCoordinates] = Field(
        default=None,
        description="Geographic coordinates"
    )
    estimated_cost: Optional[float] = Field(
        default=None,
        ge=0,
        description="Estimated cost in UAH"
    )
    duration_minutes: Optional[int] = Field(
        default=None,
        ge=15,
        le=480,
        description="Duration in minutes (15-480)"
    )
    start_time: Optional[str] = Field(
        default=None,
        description="Suggested start time (HH:MM format)",
        pattern=r"^([01]?[0-9]|2[0-3]):[0-5][0-9]$"
    )
    category: Optional[str] = Field(
        default=None,
        description="Activity category: food, culture, nature, etc."
    )
    rationale: str = Field(
        ...,
        min_length=10,
        max_length=500,
        description="Explanation why this place was chosen"
    )


class TripPlan(BaseModel):
    """Complete trip plan response."""
    
    title: str = Field(
        ...,
        min_length=5,
        max_length=200,
        description="Trip title"
    )
    summary: str = Field(
        ...,
        min_length=20,
        max_length=1000,
        description="Trip summary/overview"
    )
    destination: str = Field(
        ...,
        description="Main destination city"
    )
    total_budget_estimate: float = Field(
        ...,
        ge=0,
        description="Total estimated budget"
    )
    currency: str = Field(
        default="UAH",
        description="Currency code"
    )
    duration_days: int = Field(
        ...,
        ge=1,
        le=15,
        description="Total duration in days"
    )
    itinerary: List[ItineraryItem] = Field(
        ...,
        min_length=1,
        description="List of itinerary items"
    )
    tags: List[str] = Field(
        default=[],
        description="Trip tags: Relaxing, Cultural, Adventure, etc."
    )
    tips: Optional[List[str]] = Field(
        default=None,
        description="Travel tips for this trip"
    )
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "title": "Культурний вікенд у Львові",
                    "summary": "Тридня подорож історичним центром Львова з відвідуванням музеїв, кав'ярень та автентичних ресторанів.",
                    "destination": "Львів",
                    "total_budget_estimate": 12000,
                    "currency": "UAH",
                    "duration_days": 3,
                    "itinerary": [
                        {
                            "day_index": 1,
                            "order_index": 1,
                            "title": "Сніданок у кав'ярні Львівська Копальня Кави",
                            "description": "Почніть день з ароматної кави та традиційного львівського сніданку",
                            "place_name": "Львівська Копальня Кави",
                            "coordinates": {"lat": 49.8419, "lng": 24.0316},
                            "estimated_cost": 350,
                            "duration_minutes": 60,
                            "start_time": "09:00",
                            "category": "food",
                            "rationale": "Культова кав'ярня Львова з унікальною атмосферою, ідеальне місце для початку дня"
                        }
                    ],
                    "tags": ["Культурний", "Гастрономічний", "Історичний"],
                    "tips": ["Носіть зручне взуття - у Львові багато бруківки", "Бронюйте столики заздалегідь"]
                }
            ]
        }
    }


class ExplainResponse(BaseModel):
    """Response for /explain endpoint."""
    
    explanation: str = Field(
        ...,
        description="Detailed explanation of the trip plan"
    )
    highlights: List[str] = Field(
        default=[],
        description="Key highlights of the plan"
    )
    answered_question: Optional[str] = Field(
        default=None,
        description="Answer to specific user question if provided"
    )


class ImproveResponse(BaseModel):
    """Response for /improve endpoint."""
    
    improved_plan: TripPlan = Field(
        ...,
        description="Improved trip plan"
    )
    changes_made: List[str] = Field(
        default=[],
        description="List of changes made to the plan"
    )
    improvement_summary: str = Field(
        ...,
        description="Summary of improvements"
    )

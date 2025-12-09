from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from datetime import date


class UserPreferences(BaseModel):
    """User preferences for trip generation."""
    
    interests: List[str] = Field(
        ...,
        description="User interests: ['history', 'food', 'nature', 'culture', 'shopping', 'nightlife']",
        min_length=1,
        max_length=10,
        examples=[["history", "food", "nature"]]
    )
    transport_modes: List[str] = Field(
        default=["walking", "public_transport"],
        description="Preferred transport modes: ['walking', 'car', 'public_transport', 'taxi', 'bicycle']",
        examples=[["walking", "public_transport"]]
    )
    avg_daily_budget: Optional[int] = Field(
        default=None,
        description="Average daily budget in UAH",
        ge=0,
        examples=[2000]
    )
    
    @field_validator("interests", "transport_modes", mode="before")
    @classmethod
    def lowercase_list(cls, v: List[str]) -> List[str]:
        """Convert all items to lowercase."""
        if isinstance(v, list):
            return [item.lower().strip() for item in v]
        return v


class TripConstraints(BaseModel):
    """Trip constraints and parameters."""
    
    origin_city: str = Field(
        ...,
        description="Starting city of the trip",
        min_length=2,
        max_length=100,
        examples=["Київ"]
    )
    destination_city: Optional[str] = Field(
        default=None,
        description="Destination city (if different from origin)",
        max_length=100,
        examples=["Львів"]
    )
    start_date: Optional[date] = Field(
        default=None,
        description="Trip start date",
        examples=["2024-12-15"]
    )
    end_date: Optional[date] = Field(
        default=None,
        description="Trip end date",
        examples=["2024-12-17"]
    )
    duration_days: int = Field(
        ...,
        ge=1,
        le=15,
        description="Trip duration in days (1-15)",
        examples=[3]
    )
    total_budget: Optional[int] = Field(
        default=None,
        description="Total trip budget in UAH",
        ge=0,
        examples=[15000]
    )
    travel_party_size: int = Field(
        default=1,
        ge=1,
        le=20,
        description="Number of travelers",
        examples=[2]
    )
    
    @field_validator("destination_city", mode="before")
    @classmethod
    def set_destination_default(cls, v, info):
        """If destination is not set, use origin city."""
        return v if v else None


class RecommendationRequest(BaseModel):
    """Request model for generating travel itinerary."""
    
    user_id: str = Field(
        ...,
        description="User UUID",
        examples=["550e8400-e29b-41d4-a716-446655440000"]
    )
    user_profile: UserPreferences
    constraints: TripConstraints
    timezone: str = Field(
        default="Europe/Kyiv",
        description="User timezone",
        examples=["Europe/Kyiv"]
    )
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "user_id": "550e8400-e29b-41d4-a716-446655440000",
                    "user_profile": {
                        "interests": ["history", "food", "culture"],
                        "transport_modes": ["walking", "public_transport"],
                        "avg_daily_budget": 2000
                    },
                    "constraints": {
                        "origin_city": "Київ",
                        "destination_city": "Львів",
                        "duration_days": 3,
                        "total_budget": 15000,
                        "travel_party_size": 2
                    },
                    "timezone": "Europe/Kyiv"
                }
            ]
        }
    }


class ExplainRequest(BaseModel):
    """Request model for explaining a trip plan."""
    
    user_id: str = Field(..., description="User UUID")
    trip_id: str = Field(..., description="Trip UUID to explain")
    question: Optional[str] = Field(
        default=None,
        description="Specific question about the trip",
        max_length=500,
        examples=["Чому обрано саме цей ресторан?"]
    )


class ImproveRequest(BaseModel):
    """Request model for improving an existing trip plan."""
    
    user_id: str = Field(..., description="User UUID")
    trip_id: str = Field(..., description="Trip UUID to improve")
    current_plan: dict = Field(
        ...,
        description="Current trip plan JSON"
    )
    improvement_request: str = Field(
        ...,
        description="What to improve",
        min_length=5,
        max_length=1000,
        examples=["Додай більше ресторанів української кухні"]
    )
    constraints: Optional[TripConstraints] = Field(
        default=None,
        description="Updated constraints (optional)"
    )

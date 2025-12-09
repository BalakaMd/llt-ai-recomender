"""Schemas module - Pydantic models for request/response validation."""
from app.schemas.request import (
    RecommendationRequest,
    ExplainRequest,
    ImproveRequest,
    UserPreferences,
    TripConstraints,
)
from app.schemas.response import (
    TripPlan,
    ItineraryItem,
    GeoCoordinates,
    ExplainResponse,
    ImproveResponse,
)

__all__ = [
    # Request schemas
    "RecommendationRequest",
    "ExplainRequest", 
    "ImproveRequest",
    "UserPreferences",
    "TripConstraints",
    # Response schemas
    "TripPlan",
    "ItineraryItem",
    "GeoCoordinates",
    "ExplainResponse",
    "ImproveResponse",
]

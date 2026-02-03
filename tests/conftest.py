"""Pytest configuration and fixtures."""
import pytest
from datetime import date, datetime
from uuid import uuid4

from app.schemas.request import (
    UserPreferences, 
    TripConstraints, 
    RecommendationRequest,
    ExplainRequest,
    ImproveRequest,
    PartialTripConstraints
)
from app.schemas.response import (
    GeoCoordinates,
    ItineraryItem,
    TripPlan,
    ExplainResponse,
    ImproveResponse
)


@pytest.fixture
def sample_user_preferences():
    """Sample user preferences for testing."""
    return UserPreferences(
        interests=["history", "food", "culture"],
        transport_modes=["walking", "public_transport"],
        avg_daily_budget=2000
    )


@pytest.fixture
def sample_trip_constraints():
    """Sample trip constraints for testing."""
    return TripConstraints(
        origin_city="Київ",
        destination_city="Львів",
        start_date=date(2024, 12, 15),
        end_date=date(2024, 12, 17),
        duration_days=3,
        total_budget=15000,
        travel_party_size=2
    )


@pytest.fixture
def sample_recommendation_request(sample_user_preferences, sample_trip_constraints):
    """Sample recommendation request for testing."""
    return RecommendationRequest(
        user_id=str(uuid4()),
        user_profile=sample_user_preferences,
        constraints=sample_trip_constraints,
        timezone="Europe/Kyiv",
        currency="UAH",
        language="Ukrainian"
    )


@pytest.fixture
def sample_geo_coordinates():
    """Sample geo coordinates for testing."""
    return GeoCoordinates(lat=49.8419, lng=24.0316)


@pytest.fixture
def sample_itinerary_item(sample_geo_coordinates):
    """Sample itinerary item for testing."""
    return ItineraryItem(
        day_index=1,
        order_index=1,
        title="Сніданок у кав'ярні",
        description="Почніть день з ароматної кави та традиційного львівського сніданку",
        place_name="Львівська Копальня Кави",
        coordinates=sample_geo_coordinates,
        estimated_cost=350.0,
        duration_minutes=60,
        start_time="09:00",
        category="food",
        rationale="Культова кав'ярня Львова з унікальною атмосферою"
    )


@pytest.fixture
def sample_trip_plan(sample_itinerary_item):
    """Sample trip plan for testing."""
    return TripPlan(
        title="Культурний вікенд у Львові",
        summary="Тридня подорож історичним центром Львова з відвідуванням музеїв",
        destination="Львів",
        total_budget_estimate=12000.0,
        currency="UAH",
        duration_days=3,
        itinerary=[sample_itinerary_item],
        tags=["Культурний", "Гастрономічний"],
        tips=["Носіть зручне взуття"]
    )


@pytest.fixture
def sample_explain_request():
    """Sample explain request for testing."""
    return ExplainRequest(
        user_id=uuid4(),
        trip_id=uuid4(),
        trip_plan={"title": "Test Trip"},
        question="Чому обрано саме цей ресторан?"
    )


@pytest.fixture
def sample_improve_request():
    """Sample improve request for testing."""
    return ImproveRequest(
        user_id=uuid4(),
        trip_id=uuid4(),
        current_plan={"title": "Test Trip"},
        improvement_request="Додай більше ресторанів української кухні",
        constraints=PartialTripConstraints(
            duration_days=4,
            total_budget=20000
        )
    )

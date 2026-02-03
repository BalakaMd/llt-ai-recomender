"""Unit tests for request schemas."""
import pytest
from datetime import date
from uuid import uuid4
from pydantic import ValidationError

from app.schemas.request import (
    UserPreferences,
    TripConstraints,
    RecommendationRequest,
    ExplainRequest,
    ImproveRequest,
    PartialTripConstraints
)


class TestUserPreferences:
    """Test cases for UserPreferences schema."""

    def test_valid_user_preferences(self):
        """Test creating valid UserPreferences."""
        prefs = UserPreferences(
            interests=["history", "food", "culture"],
            transport_modes=["walking", "public_transport"],
            avg_daily_budget=2000
        )
        
        assert prefs.interests == ["history", "food", "culture"]
        assert prefs.transport_modes == ["walking", "public_transport"]
        assert prefs.avg_daily_budget == 2000

    def test_lowercase_validator(self):
        """Test that list items are converted to lowercase."""
        prefs = UserPreferences(
            interests=["HISTORY", "Food", "CULTURE"],
            transport_modes=["WALKING", "PUBLIC_TRANSPORT"]
        )
        
        assert prefs.interests == ["history", "food", "culture"]
        assert prefs.transport_modes == ["walking", "public_transport"]

    def test_interests_validation(self):
        """Test interests field validation."""
        # Empty interests should fail
        with pytest.raises(ValidationError):
            UserPreferences(interests=[], transport_modes=["walking"])
        
        # Too many interests should fail
        with pytest.raises(ValidationError):
            UserPreferences(
                interests=["history"] * 11,  # 11 items, max is 10
                transport_modes=["walking"]
            )

    def test_transport_modes_default(self):
        """Test default transport modes."""
        prefs = UserPreferences(interests=["history"])
        assert prefs.transport_modes == ["walking", "public_transport"]

    def test_budget_validation(self):
        """Test budget validation."""
        # Negative budget should fail
        with pytest.raises(ValidationError):
            UserPreferences(
                interests=["history"],
                avg_daily_budget=-100
            )
        
        # Zero budget should pass
        prefs = UserPreferences(interests=["history"], avg_daily_budget=0)
        assert prefs.avg_daily_budget == 0


class TestTripConstraints:
    """Test cases for TripConstraints schema."""

    def test_valid_trip_constraints(self):
        """Test creating valid TripConstraints."""
        constraints = TripConstraints(
            origin_city="Київ",
            destination_city="Львів",
            start_date=date(2024, 12, 15),
            end_date=date(2024, 12, 17),
            duration_days=3,
            total_budget=15000,
            travel_party_size=2
        )
        
        assert constraints.origin_city == "Київ"
        assert constraints.destination_city == "Львів"
        assert constraints.duration_days == 3
        assert constraints.travel_party_size == 2

    def test_duration_validation(self):
        """Test duration days validation."""
        # Duration too short
        with pytest.raises(ValidationError):
            TripConstraints(origin_city="Київ", duration_days=0)
        
        # Duration too long
        with pytest.raises(ValidationError):
            TripConstraints(origin_city="Київ", duration_days=16)

    def test_travel_party_size_validation(self):
        """Test travel party size validation."""
        # Party size too small
        with pytest.raises(ValidationError):
            TripConstraints(origin_city="Київ", duration_days=3, travel_party_size=0)
        
        # Party size too large
        with pytest.raises(ValidationError):
            TripConstraints(origin_city="Київ", duration_days=3, travel_party_size=21)

    def test_destination_default(self):
        """Test that destination defaults to None when not provided."""
        constraints = TripConstraints(origin_city="Київ", duration_days=3)
        assert constraints.destination_city is None

    def test_city_length_validation(self):
        """Test city name length validation."""
        # Origin city too short
        with pytest.raises(ValidationError):
            TripConstraints(origin_city="К", duration_days=3)
        
        # Origin city too long
        with pytest.raises(ValidationError):
            TripConstraints(origin_city="К" * 101, duration_days=3)

    def test_budget_validation(self):
        """Test total budget validation."""
        # Negative budget should fail
        with pytest.raises(ValidationError):
            TripConstraints(
                origin_city="Київ",
                duration_days=3,
                total_budget=-100
            )


class TestRecommendationRequest:
    """Test cases for RecommendationRequest schema."""

    def test_valid_recommendation_request(self, sample_user_preferences, sample_trip_constraints):
        """Test creating valid RecommendationRequest."""
        request = RecommendationRequest(
            user_id=str(uuid4()),
            user_profile=sample_user_preferences,
            constraints=sample_trip_constraints
        )
        
        assert request.user_id is not None
        assert request.user_profile == sample_user_preferences
        assert request.constraints == sample_trip_constraints
        assert request.timezone == "Europe/Kyiv"
        assert request.currency == "UAH"
        assert request.language == "Ukrainian"

    def test_custom_fields(self, sample_user_preferences, sample_trip_constraints):
        """Test RecommendationRequest with custom field values."""
        user_id = str(uuid4())
        request = RecommendationRequest(
            user_id=user_id,
            user_profile=sample_user_preferences,
            constraints=sample_trip_constraints,
            timezone="America/New_York",
            currency="USD",
            language="English"
        )
        
        assert request.timezone == "America/New_York"
        assert request.currency == "USD"
        assert request.language == "English"


class TestExplainRequest:
    """Test cases for ExplainRequest schema."""

    def test_valid_explain_request(self):
        """Test creating valid ExplainRequest."""
        request = ExplainRequest(
            user_id=uuid4(),
            trip_id=uuid4(),
            trip_plan={"title": "Test Trip", "days": []},
            question="Чому обрано саме цей ресторан?"
        )
        
        assert request.user_id is not None
        assert request.trip_id is not None
        assert request.trip_plan == {"title": "Test Trip", "days": []}
        assert request.question == "Чому обрано саме цей ресторан?"

    def test_explain_request_without_question(self):
        """Test ExplainRequest without optional question."""
        request = ExplainRequest(
            user_id=uuid4(),
            trip_id=uuid4(),
            trip_plan={"title": "Test Trip"}
        )
        
        assert request.question is None

    def test_question_length_validation(self):
        """Test question length validation."""
        # Question too long
        with pytest.raises(ValidationError):
            ExplainRequest(
                user_id=uuid4(),
                trip_id=uuid4(),
                trip_plan={"title": "Test Trip"},
                question="q" * 501  # 501 chars, max is 500
            )


class TestImproveRequest:
    """Test cases for ImproveRequest schema."""

    def test_valid_improve_request(self):
        """Test creating valid ImproveRequest."""
        request = ImproveRequest(
            user_id=uuid4(),
            trip_id=uuid4(),
            current_plan={"title": "Test Trip"},
            improvement_request="Додай більше ресторанів української кухні"
        )
        
        assert request.user_id is not None
        assert request.trip_id is not None
        assert request.current_plan == {"title": "Test Trip"}
        assert request.improvement_request == "Додай більше ресторанів української кухні"

    def test_improvement_request_validation(self):
        """Test improvement request validation."""
        # Request too short
        with pytest.raises(ValidationError):
            ImproveRequest(
                user_id=uuid4(),
                trip_id=uuid4(),
                current_plan={"title": "Test Trip"},
                improvement_request="1234"  # 4 chars, min is 5
            )
        
        # Request too long
        with pytest.raises(ValidationError):
            ImproveRequest(
                user_id=uuid4(),
                trip_id=uuid4(),
                current_plan={"title": "Test Trip"},
                improvement_request="д" * 1001  # 1001 chars, max is 1000
            )

    def test_improve_request_with_constraints(self):
        """Test ImproveRequest with optional constraints."""
        constraints = PartialTripConstraints(
            duration_days=4,
            total_budget=20000
        )
        
        request = ImproveRequest(
            user_id=uuid4(),
            trip_id=uuid4(),
            current_plan={"title": "Test Trip"},
            improvement_request="Додай більше ресторанів",
            constraints=constraints
        )
        
        assert request.constraints == constraints


class TestPartialTripConstraints:
    """Test cases for PartialTripConstraints schema."""

    def test_empty_partial_constraints(self):
        """Test creating empty PartialTripConstraints."""
        constraints = PartialTripConstraints()
        
        assert constraints.origin_city is None
        assert constraints.destination_city is None
        assert constraints.start_date is None
        assert constraints.end_date is None
        assert constraints.duration_days is None
        assert constraints.total_budget is None
        assert constraints.travel_party_size is None

    def test_partial_constraints_with_some_fields(self):
        """Test PartialTripConstraints with some fields."""
        constraints = PartialTripConstraints(
            duration_days=4,
            total_budget=20000
        )
        
        assert constraints.duration_days == 4
        assert constraints.total_budget == 20000
        assert constraints.origin_city is None

    def test_partial_constraints_validation(self):
        """Test PartialTripConstraints validation."""
        # Invalid duration should still fail
        with pytest.raises(ValidationError):
            PartialTripConstraints(duration_days=0)
        
        # Invalid budget should still fail
        with pytest.raises(ValidationError):
            PartialTripConstraints(total_budget=-100)

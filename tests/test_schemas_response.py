"""Unit tests for response schemas."""
import pytest
from pydantic import ValidationError

from app.schemas.response import (
    GeoCoordinates,
    ItineraryItem,
    TripPlan,
    ExplainResponse,
    ImproveResponse
)


class TestGeoCoordinates:
    """Test cases for GeoCoordinates schema."""

    def test_valid_coordinates(self):
        """Test creating valid GeoCoordinates."""
        coords = GeoCoordinates(lat=49.8419, lng=24.0316)
        
        assert coords.lat == 49.8419
        assert coords.lng == 24.0316

    def test_latitude_validation(self):
        """Test latitude validation."""
        # Latitude too high
        with pytest.raises(ValidationError):
            GeoCoordinates(lat=90.1, lng=0)
        
        # Latitude too low
        with pytest.raises(ValidationError):
            GeoCoordinates(lat=-90.1, lng=0)
        
        # Edge cases should pass
        coords1 = GeoCoordinates(lat=90, lng=0)
        coords2 = GeoCoordinates(lat=-90, lng=0)
        assert coords1.lat == 90
        assert coords2.lat == -90

    def test_longitude_validation(self):
        """Test longitude validation."""
        # Longitude too high
        with pytest.raises(ValidationError):
            GeoCoordinates(lat=0, lng=180.1)
        
        # Longitude too low
        with pytest.raises(ValidationError):
            GeoCoordinates(lat=0, lng=-180.1)
        
        # Edge cases should pass
        coords1 = GeoCoordinates(lat=0, lng=180)
        coords2 = GeoCoordinates(lat=0, lng=-180)
        assert coords1.lng == 180
        assert coords2.lng == -180


class TestItineraryItem:
    """Test cases for ItineraryItem schema."""

    def test_valid_itinerary_item(self, sample_geo_coordinates):
        """Test creating valid ItineraryItem."""
        item = ItineraryItem(
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
        
        assert item.day_index == 1
        assert item.order_index == 1
        assert item.title == "Сніданок у кав'ярні"
        assert item.coordinates == sample_geo_coordinates
        assert item.estimated_cost == 350.0

    def test_day_index_validation(self):
        """Test day index validation."""
        # Day index too low
        with pytest.raises(ValidationError):
            ItineraryItem(
                day_index=0,
                order_index=1,
                title="Test",
                description="Test description",
                place_name="Test place",
                rationale="Test rationale"
            )
        
        # Day index should pass
        item = ItineraryItem(
            day_index=1,
            order_index=1,
            title="Test",
            description="Test description",
            place_name="Test place",
            rationale="Test rationale"
        )
        assert item.day_index == 1

    def test_order_index_validation(self):
        """Test order index validation."""
        # Order index too low
        with pytest.raises(ValidationError):
            ItineraryItem(
                day_index=1,
                order_index=0,
                title="Test",
                description="Test description",
                place_name="Test place",
                rationale="Test rationale"
            )

    def test_title_length_validation(self):
        """Test title length validation."""
        # Title too short
        with pytest.raises(ValidationError):
            ItineraryItem(
                day_index=1,
                order_index=1,
                title="A",
                description="Test description",
                place_name="Test place",
                rationale="Test rationale"
            )
        
        # Title too long
        with pytest.raises(ValidationError):
            ItineraryItem(
                day_index=1,
                order_index=1,
                title="T" * 201,  # 201 chars, max is 200
                description="Test description",
                place_name="Test place",
                rationale="Test rationale"
            )

    def test_description_length_validation(self):
        """Test description length validation."""
        # Description too short
        with pytest.raises(ValidationError):
            ItineraryItem(
                day_index=1,
                order_index=1,
                title="Test title",
                description="Short",
                place_name="Test place",
                rationale="Test rationale"
            )
        
        # Description too long
        with pytest.raises(ValidationError):
            ItineraryItem(
                day_index=1,
                order_index=1,
                title="Test title",
                description="D" * 1001,  # 1001 chars, max is 1000
                place_name="Test place",
                rationale="Test rationale"
            )

    def test_place_name_length_validation(self):
        """Test place name length validation."""
        # Place name too short
        with pytest.raises(ValidationError):
            ItineraryItem(
                day_index=1,
                order_index=1,
                title="Test title",
                description="Test description that is long enough",
                place_name="A",
                rationale="Test rationale"
            )
        
        # Place name too long
        with pytest.raises(ValidationError):
            ItineraryItem(
                day_index=1,
                order_index=1,
                title="Test title",
                description="Test description that is long enough",
                place_name="P" * 201,  # 201 chars, max is 200
                rationale="Test rationale"
            )

    def test_cost_validation(self):
        """Test estimated cost validation."""
        # Negative cost should fail
        with pytest.raises(ValidationError):
            ItineraryItem(
                day_index=1,
                order_index=1,
                title="Test title",
                description="Test description that is long enough",
                place_name="Test place",
                estimated_cost=-10.0,
                rationale="Test rationale"
            )
        
        # Zero cost should pass
        item = ItineraryItem(
            day_index=1,
            order_index=1,
            title="Test title",
            description="Test description that is long enough",
            place_name="Test place",
            estimated_cost=0.0,
            rationale="Test rationale"
        )
        assert item.estimated_cost == 0.0

    def test_duration_validation(self):
        """Test duration minutes validation."""
        # Duration too short
        with pytest.raises(ValidationError):
            ItineraryItem(
                day_index=1,
                order_index=1,
                title="Test title",
                description="Test description that is long enough",
                place_name="Test place",
                duration_minutes=14,
                rationale="Test rationale"
            )
        
        # Duration too long
        with pytest.raises(ValidationError):
            ItineraryItem(
                day_index=1,
                order_index=1,
                title="Test title",
                description="Test description that is long enough",
                place_name="Test place",
                duration_minutes=481,
                rationale="Test rationale"
            )
        
        # Edge cases should pass
        item1 = ItineraryItem(
            day_index=1,
            order_index=1,
            title="Test title",
            description="Test description that is long enough",
            place_name="Test place",
            duration_minutes=15,
            rationale="Test rationale"
        )
        item2 = ItineraryItem(
            day_index=1,
            order_index=1,
            title="Test title",
            description="Test description that is long enough",
            place_name="Test place",
            duration_minutes=480,
            rationale="Test rationale"
        )
        assert item1.duration_minutes == 15
        assert item2.duration_minutes == 480

    def test_start_time_validation(self):
        """Test start time pattern validation."""
        # Valid times
        valid_times = ["09:00", "23:59", "00:00", "12:30", "9:00"]  # 9:00 is valid per pattern
        for time_str in valid_times:
            item = ItineraryItem(
                day_index=1,
                order_index=1,
                title="Test title",
                description="Test description that is long enough",
                place_name="Test place",
                start_time=time_str,
                rationale="Test rationale"
            )
            assert item.start_time == time_str
        
        # Invalid times
        invalid_times = ["24:00", "23:60", "09:0", "09:00:00", "ab:cd"]
        for time_str in invalid_times:
            with pytest.raises(ValidationError):
                ItineraryItem(
                    day_index=1,
                    order_index=1,
                    title="Test title",
                    description="Test description that is long enough",
                    place_name="Test place",
                    start_time=time_str,
                    rationale="Test rationale"
                )

    def test_rationale_length_validation(self):
        """Test rationale length validation."""
        # Rationale too short
        with pytest.raises(ValidationError):
            ItineraryItem(
                day_index=1,
                order_index=1,
                title="Test title",
                description="Test description that is long enough",
                place_name="Test place",
                rationale="Short"
            )
        
        # Rationale too long
        with pytest.raises(ValidationError):
            ItineraryItem(
                day_index=1,
                order_index=1,
                title="Test title",
                description="Test description that is long enough",
                place_name="Test place",
                rationale="R" * 501  # 501 chars, max is 500
            )


class TestTripPlan:
    """Test cases for TripPlan schema."""

    def test_valid_trip_plan(self, sample_itinerary_item):
        """Test creating valid TripPlan."""
        plan = TripPlan(
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
        
        assert plan.title == "Культурний вікенд у Львові"
        assert plan.destination == "Львів"
        assert plan.total_budget_estimate == 12000.0
        assert plan.currency == "UAH"
        assert len(plan.itinerary) == 1
        assert plan.tags == ["Культурний", "Гастрономічний"]
        assert plan.tips == ["Носіть зручне взуття"]

    def test_title_length_validation(self, sample_itinerary_item):
        """Test title length validation."""
        # Title too short
        with pytest.raises(ValidationError):
            TripPlan(
                title="К",
                summary="Test summary that is long enough",
                destination="Львів",
                total_budget_estimate=1000.0,
                duration_days=1,
                itinerary=[sample_itinerary_item]
            )
        
        # Title too long
        with pytest.raises(ValidationError):
            TripPlan(
                title="T" * 201,  # 201 chars, max is 200
                summary="Test summary that is long enough",
                destination="Львів",
                total_budget_estimate=1000.0,
                duration_days=1,
                itinerary=[sample_itinerary_item]
            )

    def test_summary_length_validation(self, sample_itinerary_item):
        """Test summary length validation."""
        # Summary too short
        with pytest.raises(ValidationError):
            TripPlan(
                title="Test title",
                summary="Short summary",
                destination="Львів",
                total_budget_estimate=1000.0,
                duration_days=1,
                itinerary=[sample_itinerary_item]
            )
        
        # Summary too long
        with pytest.raises(ValidationError):
            TripPlan(
                title="Test title",
                summary="S" * 1001,  # 1001 chars, max is 1000
                destination="Львів",
                total_budget_estimate=1000.0,
                duration_days=1,
                itinerary=[sample_itinerary_item]
            )

    def test_budget_validation(self, sample_itinerary_item):
        """Test total budget validation."""
        # Negative budget should fail
        with pytest.raises(ValidationError):
            TripPlan(
                title="Test title",
                summary="Test summary that is long enough",
                destination="Львів",
                total_budget_estimate=-100.0,
                duration_days=1,
                itinerary=[sample_itinerary_item]
            )
        
        # Zero budget should pass
        plan = TripPlan(
            title="Test title",
            summary="Test summary that is long enough",
            destination="Львів",
            total_budget_estimate=0.0,
            duration_days=1,
            itinerary=[sample_itinerary_item]
        )
        assert plan.total_budget_estimate == 0.0

    def test_duration_validation(self, sample_itinerary_item):
        """Test duration days validation."""
        # Duration too short
        with pytest.raises(ValidationError):
            TripPlan(
                title="Test title",
                summary="Test summary that is long enough",
                destination="Львів",
                total_budget_estimate=1000.0,
                duration_days=0,
                itinerary=[sample_itinerary_item]
            )
        
        # Duration too long
        with pytest.raises(ValidationError):
            TripPlan(
                title="Test title",
                summary="Test summary that is long enough",
                destination="Львів",
                total_budget_estimate=1000.0,
                duration_days=16,
                itinerary=[sample_itinerary_item]
            )

    def test_itinerary_validation(self, sample_itinerary_item):
        """Test itinerary validation."""
        # Empty itinerary should fail
        with pytest.raises(ValidationError):
            TripPlan(
                title="Test title",
                summary="Test summary that is long enough",
                destination="Львів",
                total_budget_estimate=1000.0,
                duration_days=1,
                itinerary=[]
            )

    def test_default_values(self, sample_itinerary_item):
        """Test default field values."""
        plan = TripPlan(
            title="Test title",
            summary="Test summary that is long enough",
            destination="Львів",
            total_budget_estimate=1000.0,
            duration_days=1,
            itinerary=[sample_itinerary_item]
        )
        
        assert plan.currency == "UAH"
        assert plan.tags == []
        assert plan.tips is None


class TestExplainResponse:
    """Test cases for ExplainResponse schema."""

    def test_valid_explain_response(self):
        """Test creating valid ExplainResponse."""
        response = ExplainResponse(
            explanation="Цей ресторан обрано через його унікальну атмосферу",
            highlights=["Автентична українська кухня", "Зручне розташування"],
            answered_question="Ресторан пропонує традиційні страви"
        )
        
        assert response.explanation == "Цей ресторан обрано через його унікальну атмосферу"
        assert response.highlights == ["Автентична українська кухня", "Зручне розташування"]
        assert response.answered_question == "Ресторан пропонує традиційні страви"

    def test_explain_response_defaults(self):
        """Test ExplainResponse with default values."""
        response = ExplainResponse(explanation="Test explanation")
        
        assert response.explanation == "Test explanation"
        assert response.highlights == []
        assert response.answered_question is None


class TestImproveResponse:
    """Test cases for ImproveResponse schema."""

    def test_valid_improve_response(self, sample_trip_plan):
        """Test creating valid ImproveResponse."""
        response = ImproveResponse(
            improved_plan=sample_trip_plan,
            changes_made=["Додано нові ресторани", "Змінено маршрут"],
            improvement_summary="План покращено з урахуванням побажань"
        )
        
        assert response.improved_plan == sample_trip_plan
        assert response.changes_made == ["Додано нові ресторани", "Змінено маршрут"]
        assert response.improvement_summary == "План покращено з урахуванням побажань"

    def test_improve_response_defaults(self, sample_trip_plan):
        """Test ImproveResponse with default values."""
        response = ImproveResponse(
            improved_plan=sample_trip_plan,
            improvement_summary="Test summary"
        )
        
        assert response.improved_plan == sample_trip_plan
        assert response.changes_made == []
        assert response.improvement_summary == "Test summary"

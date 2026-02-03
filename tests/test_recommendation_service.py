"""Unit tests for RecommendationService."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

from app.schemas.request import RecommendationRequest, ExplainRequest, ImproveRequest, UserPreferences, TripConstraints
from app.schemas.response import TripPlan, ExplainResponse, ImproveResponse
from app.services.recommendation import RecommendationService
from app.services.telemetry import TelemetryService
from app.services.integration_client import IntegrationClient
from app.services.llm_engine import LLMEngine
from app.models.ai_runs import AIRun


class TestRecommendationService:
    """Test cases for RecommendationService."""

    @pytest.fixture
    def mock_telemetry(self):
        """Mock TelemetryService."""
        telemetry = AsyncMock(spec=TelemetryService)
        telemetry.create_run = AsyncMock(return_value=MagicMock(spec=AIRun, id=uuid4()))
        telemetry.complete_run = AsyncMock()
        telemetry.fail_run = AsyncMock()
        return telemetry

    @pytest.fixture
    def mock_integration(self):
        """Mock IntegrationClient."""
        integration = AsyncMock(spec=IntegrationClient)
        integration.get_weather = AsyncMock(return_value={"temperature": 20, "condition": "sunny"})
        integration.search_pois = AsyncMock(return_value=[
            {"name": "Test POI", "category": "museum", "coordinates": {"lat": 49.8, "lng": 24.0}}
        ])
        return integration

    @pytest.fixture
    def mock_llm(self):
        """Mock LLMEngine."""
        llm = AsyncMock(spec=LLMEngine)
        llm.provider = MagicMock()
        llm.generate_itinerary = AsyncMock(return_value=(
            TripPlan(
                title="Test Trip",
                summary="Test summary that is long enough to pass validation",
                destination="Київ",
                total_budget_estimate=5000.0,
                duration_days=2,
                itinerary=[
                    {
                        "day_index": 1,
                        "order_index": 1,
                        "title": "Test Activity",
                        "description": "Test description that is long enough",
                        "place_name": "Test Place",
                        "rationale": "Test rationale that is long enough"
                    }
                ]
            ),
            150
        ))
        llm.generate_explanation = AsyncMock(return_value=(
            ExplainResponse(explanation="Test explanation"),
            50
        ))
        llm.generate_improvement = AsyncMock(return_value=(
            ImproveResponse(
                improved_plan=TripPlan(
                    title="Improved Trip",
                    summary="Improved summary that is long enough to pass validation",
                    destination="Київ",
                    total_budget_estimate=6000.0,
                    duration_days=2,
                    itinerary=[
                        {
                            "day_index": 1,
                            "order_index": 1,
                            "title": "Improved Activity",
                            "description": "Improved description that is long enough",
                            "place_name": "Improved Place",
                            "rationale": "Improved rationale that is long enough"
                        }
                    ]
                ),
                improvement_summary="Plan improved"
            ),
            100
        ))
        return llm

    @pytest.fixture
    def recommendation_service(self, mock_telemetry, mock_integration, mock_llm):
        """Create RecommendationService instance with mocked dependencies."""
        return RecommendationService(
            telemetry=mock_telemetry,
            integration=mock_integration,
            llm=mock_llm
        )

    @pytest.fixture
    def mock_background_tasks(self):
        """Mock BackgroundTasks."""
        background_tasks = MagicMock()
        background_tasks.add_task = MagicMock()
        return background_tasks

    async def test_generate_recommendation_success(
        self, 
        recommendation_service, 
        mock_telemetry, 
        mock_integration, 
        mock_llm,
        mock_background_tasks,
        sample_recommendation_request
    ):
        """Test successful recommendation generation."""
        # Execute
        result = await recommendation_service.generate_recommendation(
            sample_recommendation_request, 
            mock_background_tasks
        )

        # Verify
        assert isinstance(result, TripPlan)
        assert result.title == "Test Trip"
        assert result.destination == "Київ"

        # Verify service calls
        mock_telemetry.create_run.assert_called_once()
        mock_integration.get_weather.assert_called_once_with(
            city="Львів",
            start_date=sample_recommendation_request.constraints.start_date,
            end_date=sample_recommendation_request.constraints.end_date
        )
        mock_integration.search_pois.assert_called_once_with(
            city="Львів",
            interests=["history", "food", "culture"]
        )
        mock_llm.generate_itinerary.assert_called_once()
        mock_background_tasks.add_task.assert_called_once()

    async def test_generate_recommendation_with_origin_as_destination(
        self, 
        recommendation_service, 
        mock_integration,
        mock_background_tasks
    ):
        """Test recommendation generation when origin equals destination."""
        # Create request without destination
        request = RecommendationRequest(
            user_id=str(uuid4()),
            user_profile=UserPreferences(
                interests=["history", "food", "culture"],
                transport_modes=["walking", "public_transport"],
                avg_daily_budget=2000
            ),
            constraints=TripConstraints(
                origin_city="Київ",
                duration_days=3
            )
        )

        # Execute
        await recommendation_service.generate_recommendation(request, mock_background_tasks)

        # Verify integration calls use origin city
        mock_integration.get_weather.assert_called_once_with(
            city="Київ",
            start_date=None,
            end_date=None
        )
        mock_integration.search_pois.assert_called_once_with(
            city="Київ",
            interests=["history", "food", "culture"]
        )

    async def test_generate_recommendation_failure(
        self, 
        recommendation_service, 
        mock_telemetry, 
        mock_integration,
        mock_background_tasks,
        sample_recommendation_request
    ):
        """Test recommendation generation failure handling."""
        # Make integration service raise an exception
        mock_integration.get_weather.side_effect = Exception("Service unavailable")

        # Execute and verify exception
        with pytest.raises(Exception, match="Service unavailable"):
            await recommendation_service.generate_recommendation(
                sample_recommendation_request, 
                mock_background_tasks
            )

        # Verify failure logging
        mock_telemetry.fail_run.assert_called_once()
        assert mock_background_tasks.add_task.call_count == 0

    async def test_explain_itinerary_success(
        self, 
        recommendation_service, 
        mock_telemetry, 
        mock_llm,
        mock_background_tasks,
        sample_explain_request
    ):
        """Test successful itinerary explanation."""
        # Execute
        result = await recommendation_service.explain_itinerary(
            sample_explain_request, 
            mock_background_tasks
        )

        # Verify
        assert isinstance(result, ExplainResponse)
        assert result.explanation == "Test explanation"

        # Verify service calls
        mock_telemetry.create_run.assert_called_once_with(
            user_id=str(sample_explain_request.user_id),
            provider=mock_llm.provider,
            prompt=f"Explain trip {sample_explain_request.trip_id}: {sample_explain_request.question}",
            trip_id=str(sample_explain_request.trip_id)
        )
        mock_llm.generate_explanation.assert_called_once()
        mock_background_tasks.add_task.assert_called_once()

    async def test_explain_itinerary_without_question(
        self, 
        recommendation_service, 
        mock_telemetry,
        mock_background_tasks
    ):
        """Test itinerary explanation without specific question."""
        request = ExplainRequest(
            user_id=uuid4(),
            trip_id=uuid4(),
            trip_plan={"title": "Test Trip"}
        )

        # Execute
        await recommendation_service.explain_itinerary(request, mock_background_tasks)

        # Verify prompt format
        mock_telemetry.create_run.assert_called_once()
        call_args = mock_telemetry.create_run.call_args
        assert "General explanation" in call_args.kwargs["prompt"]

    async def test_explain_itinerary_failure(
        self, 
        recommendation_service, 
        mock_telemetry, 
        mock_llm,
        mock_background_tasks,
        sample_explain_request
    ):
        """Test itinerary explanation failure handling."""
        # Make LLM service raise an exception
        mock_llm.generate_explanation.side_effect = Exception("LLM error")

        # Execute and verify exception
        with pytest.raises(Exception, match="LLM error"):
            await recommendation_service.explain_itinerary(
                sample_explain_request, 
                mock_background_tasks
            )

        # Verify failure logging
        mock_telemetry.fail_run.assert_called_once()
        assert mock_background_tasks.add_task.call_count == 0

    async def test_improve_itinerary_success(
        self, 
        recommendation_service, 
        mock_telemetry, 
        mock_llm,
        mock_background_tasks,
        sample_improve_request
    ):
        """Test successful itinerary improvement."""
        # Execute
        result = await recommendation_service.improve_itinerary(
            sample_improve_request, 
            mock_background_tasks
        )

        # Verify
        assert isinstance(result, ImproveResponse)
        assert result.improvement_summary == "Plan improved"
        assert isinstance(result.improved_plan, TripPlan)

        # Verify service calls
        mock_telemetry.create_run.assert_called_once_with(
            user_id=str(sample_improve_request.user_id),
            provider=mock_llm.provider,
            prompt=f"Improve trip {sample_improve_request.trip_id}: {sample_improve_request.improvement_request}",
            trip_id=str(sample_improve_request.trip_id)
        )
        mock_llm.generate_improvement.assert_called_once()
        mock_background_tasks.add_task.assert_called_once()

    async def test_improve_itinerary_without_constraints(
        self, 
        recommendation_service, 
        mock_llm,
        mock_background_tasks
    ):
        """Test itinerary improvement without constraints."""
        request = ImproveRequest(
            user_id=uuid4(),
            trip_id=uuid4(),
            current_plan={"title": "Test Trip"},
            improvement_request="Додай більше ресторанів"
        )

        # Execute
        await recommendation_service.improve_itinerary(request, mock_background_tasks)

        # Verify LLM call with None constraints
        mock_llm.generate_improvement.assert_called_once()
        call_args = mock_llm.generate_improvement.call_args
        assert call_args.kwargs["user_prompt"] is not None

    async def test_improve_itinerary_failure(
        self, 
        recommendation_service, 
        mock_telemetry, 
        mock_llm,
        mock_background_tasks,
        sample_improve_request
    ):
        """Test itinerary improvement failure handling."""
        # Make LLM service raise an exception
        mock_llm.generate_improvement.side_effect = Exception("LLM error")

        # Execute and verify exception
        with pytest.raises(Exception, match="LLM error"):
            await recommendation_service.improve_itinerary(
                sample_improve_request, 
                mock_background_tasks
            )

        # Verify failure logging
        mock_telemetry.fail_run.assert_called_once()
        assert mock_background_tasks.add_task.call_count == 0

    @pytest.mark.asyncio
    async def test_service_initialization(self, mock_telemetry, mock_integration, mock_llm):
        """Test RecommendationService initialization."""
        service = RecommendationService(
            telemetry=mock_telemetry,
            integration=mock_integration,
            llm=mock_llm
        )

        assert service.telemetry == mock_telemetry
        assert service.integration == mock_integration
        assert service.llm == mock_llm

from typing import Annotated

from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException, status

from app.api.deps import verify_token, get_recommendation_service
from app.schemas.request import RecommendationRequest, ExplainRequest, ImproveRequest
from app.schemas.response import TripPlan, ExplainResponse, ImproveResponse
from app.services.recommendation import RecommendationService


router = APIRouter(
    prefix="/internal/v1/ai",
    tags=["AI Recommender"],
    dependencies=[Depends(verify_token)],
)


@router.post("/recommend", response_model=TripPlan)
async def generate_recommendation(
    request: RecommendationRequest,
    background_tasks: BackgroundTasks,
    service: Annotated[RecommendationService, Depends(get_recommendation_service)],
):
    """Generate a personalized travel itinerary."""
    return await service.generate_recommendation(request, background_tasks)


@router.post("/explain", response_model=ExplainResponse)
async def explain_itinerary(
    request: ExplainRequest,
    background_tasks: BackgroundTasks,
    service: Annotated[RecommendationService, Depends(get_recommendation_service)],
):
    """Explain a specific trip plan or answer questions about it."""
    return await service.explain_itinerary(request, background_tasks)


@router.post("/improve", response_model=ImproveResponse)
async def improve_itinerary(
    request: ImproveRequest,
    background_tasks: BackgroundTasks,
    service: Annotated[RecommendationService, Depends(get_recommendation_service)],
):
    """Improve an existing travel itinerary."""
    return await service.improve_itinerary(request, background_tasks)

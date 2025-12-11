from typing import Optional, Dict, Any, List

from fastapi import BackgroundTasks

from app.schemas.request import RecommendationRequest, ExplainRequest, ImproveRequest
from app.schemas.response import TripPlan, ExplainResponse, ImproveResponse
from app.services.telemetry import TelemetryService
from app.services.integration_client import MockIntegrationClient
from app.services.llm_engine import LLMEngine
from app.services.prompts import PromptBuilder


class RecommendationService:
    """Service for handling travel recommendation business logic."""

    def __init__(
        self,
        telemetry: TelemetryService,
        integration: MockIntegrationClient,
        llm: LLMEngine,
    ):
        self.telemetry = telemetry
        self.integration = integration
        self.llm = llm

    async def generate_recommendation(
        self, 
        request: RecommendationRequest, 
        background_tasks: BackgroundTasks
    ) -> TripPlan:
        """Generate a personalized travel itinerary."""
        
        # 1. Create run record (PENDING)
        initial_prompt_log = f"Generate itinerary for {request.constraints.destination_city or request.constraints.origin_city}"
        
        run = await self.telemetry.create_run(
            user_id=request.user_id,
            provider=self.llm.provider,
            prompt=initial_prompt_log, 
        )
        
        try:
            # 2. Fetch context data (Weather, POIs)
            city = request.constraints.destination_city or request.constraints.origin_city
            interests = request.user_profile.interests
            
            weather = await self.integration.get_weather(
                city=city, 
                start_date=request.constraints.start_date,
                end_date=request.constraints.end_date
            )
            pois = await self.integration.search_pois(city=city, interests=interests)
            
            # TODO Get language and currency from request/user_profile
            # 3. Build Prompts
            prompts = PromptBuilder.build_recommendation_prompt(
                preferences=request.user_profile.model_dump(),
                constraints=request.constraints.model_dump(),
                weather=weather,
                pois=pois,
                language="Ukrainian",
                currency="UAH"
            )
            
            # 4. Generate with LLM
            trip_plan, tokens = await self.llm.generate_itinerary(
                system_prompt=prompts["system"],
                user_prompt=prompts["user"]
            )
            
            # 5. Log completion (Background)
            background_tasks.add_task(
                self.telemetry.complete_run,
                run_id=run.id,
                response=trip_plan.model_dump(),
                tokens_used=tokens
            )
            
            return trip_plan

        except Exception as e:
            # 6. Log failure
            await self.telemetry.fail_run(run_id=run.id, error_message=str(e))
            raise e

    async def explain_itinerary(
        self, 
        request: ExplainRequest, 
        background_tasks: BackgroundTasks
    ) -> ExplainResponse:
        """Explain a specific trip plan."""
        
        run = await self.telemetry.create_run(
            user_id=str(request.user_id),
            provider=self.llm.provider,
            prompt=f"Explain trip {request.trip_id}: {request.question or 'General explanation'}",
            trip_id=str(request.trip_id)
        )
        
        try:
            # TODO Get language from request/user_profile
            # Build Prompts
            prompts = PromptBuilder.build_explain_prompt(
                trip_plan=request.trip_plan,
                question=request.question,
                language="Ukrainian"
            )
            
            # Generate
            explain_response, tokens = await self.llm.generate_explanation(
                system_prompt=prompts["system"],
                user_prompt=prompts["user"]
            )
            
            # Log completion
            background_tasks.add_task(
                self.telemetry.complete_run,
                run_id=run.id,
                response=explain_response.model_dump(),
                tokens_used=tokens
            )
            
            return explain_response
            
        except Exception as e:
            await self.telemetry.fail_run(run_id=run.id, error_message=str(e))
            raise e

    async def improve_itinerary(
        self, 
        request: ImproveRequest, 
        background_tasks: BackgroundTasks
    ) -> ImproveResponse:
        """Improve an existing travel itinerary."""
        
        run = await self.telemetry.create_run(
            user_id=str(request.user_id),
            provider=self.llm.provider,
            prompt=f"Improve trip {request.trip_id}: {request.improvement_request}",
            trip_id=str(request.trip_id)
        )
        
        try:
            # TODO Get language and currency from request/user_profile
            # Build Prompts
            prompts = PromptBuilder.build_improve_prompt(
                current_plan=request.current_plan,
                improvement_request=request.improvement_request,
                constraints=request.constraints.model_dump() if request.constraints else None,
                language="Ukrainian",
                currency="UAH"
            )
            
            # Generate
            improve_response, tokens = await self.llm.generate_improvement(
                system_prompt=prompts["system"],
                user_prompt=prompts["user"]
            )
            
            # Log completion
            background_tasks.add_task(
                self.telemetry.complete_run,
                run_id=run.id,
                response=improve_response.model_dump(),
                tokens_used=tokens
            )
            
            return improve_response
            
        except Exception as e:
            await self.telemetry.fail_run(run_id=run.id, error_message=str(e))
            raise e

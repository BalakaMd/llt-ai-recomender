import json
from typing import List, Dict, Any, Optional

from app.services.prompt_templates import (
    RECOMMENDATION_SYSTEM_PROMPT,
    RECOMMENDATION_SYSTEM_JSON_SCHEMA,
    RECOMMENDATION_USER_PROMPT,
    EXPLAIN_SYSTEM_PROMPT,
    EXPLAIN_SYSTEM_PROMPT_JSON_SCHEMA,
    EXPLAIN_USER_PROMPT,
    IMPROVE_SYSTEM_PROMPT,
    IMPROVE_USER_PROMPT,
)


class PromptBuilder:
    """Builder for LLM prompts with language and currency support."""
    
    DEFAULT_LANGUAGE = "Ukrainian"
    DEFAULT_CURRENCY = "UAH"
    
    @staticmethod
    def build_recommendation_prompt(
        preferences: Dict[str, Any],
        constraints: Dict[str, Any],
        weather: Dict[str, Any],
        pois: List[Dict[str, Any]],
        language: str = DEFAULT_LANGUAGE,
        currency: str = DEFAULT_CURRENCY,
    ) -> Dict[str, str]:
        """Build system and user prompts for itinerary generation."""
        
        # Format weather context
        weather_context = ""
        if weather and weather.get("forecast"):
            weather_context = f"\nWEATHER FORECAST for {weather.get('city', 'destination')}:\n{json.dumps(weather['forecast'], ensure_ascii=False, indent=2)}"
        
        # Format POIs context
        pois_context = ""
        if pois:
            pois_context = f"\nAVAILABLE PLACES (Points of Interest):\n{json.dumps(pois[:15], ensure_ascii=False, indent=2)}"
        
        json_schema = RECOMMENDATION_SYSTEM_JSON_SCHEMA.format(currency=currency)
        system_prompt = RECOMMENDATION_SYSTEM_PROMPT.format(
            language=language,
            currency=currency,
            json_schema=json_schema,
        )
        
        user_prompt = RECOMMENDATION_USER_PROMPT.format(
            interests=", ".join(preferences.get("interests", [])),
            transport_modes=", ".join(preferences.get("transport_modes", ["walking"])),
            daily_budget=preferences.get("avg_daily_budget", "not specified"),
            currency=currency,
            origin_city=constraints.get("origin_city", "not specified"),
            destination_city=constraints.get("destination_city") or constraints.get("origin_city", "not specified"),
            duration_days=constraints.get("duration_days", 3),
            total_budget=constraints.get("total_budget", "not specified"),
            party_size=constraints.get("travel_party_size", 1),
            weather_context=weather_context,
            pois_context=pois_context,
            language=language,
        )
        
        return {"system": system_prompt, "user": user_prompt}
    
    @staticmethod
    def build_explain_prompt(
        trip_plan: Dict[str, Any],
        question: Optional[str] = None,
        language: str = DEFAULT_LANGUAGE,
    ) -> Dict[str, str]:
        """Build prompts for explaining a trip plan."""
        
        question_context = f"USER QUESTION: {question}" if question else "Provide a general explanation of the itinerary."
        
        system_prompt = EXPLAIN_SYSTEM_PROMPT.format(
            language=language,
            json_schema=EXPLAIN_SYSTEM_PROMPT_JSON_SCHEMA,
        )
        
        user_prompt = EXPLAIN_USER_PROMPT.format(
            trip_plan=json.dumps(trip_plan, ensure_ascii=False, indent=2),
            question_context=question_context,
            language=language,
        )
        
        return {"system": system_prompt, "user": user_prompt}
    
    @staticmethod
    def build_improve_prompt(
        current_plan: Dict[str, Any],
        improvement_request: str,
        constraints: Optional[Dict[str, Any]] = None,
        language: str = DEFAULT_LANGUAGE,
        currency: str = DEFAULT_CURRENCY,
    ) -> Dict[str, str]:
        """Build prompts for improving a trip plan."""
        
        constraints_context = ""
        if constraints:
            constraints_context = f"\nNEW CONSTRAINTS:\n{json.dumps(constraints, ensure_ascii=False, indent=2)}"
        
        system_prompt = IMPROVE_SYSTEM_PROMPT.format(
            language=language,
            currency=currency,
        )
        
        user_prompt = IMPROVE_USER_PROMPT.format(
            current_plan=json.dumps(current_plan, ensure_ascii=False, indent=2),
            improvement_request=improvement_request,
            constraints_context=constraints_context,
            language=language,
            currency=currency,
        )
        
        return {"system": system_prompt, "user": user_prompt}

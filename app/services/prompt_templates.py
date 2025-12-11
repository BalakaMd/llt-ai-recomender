# System prompt for itinerary generation
RECOMMENDATION_SYSTEM_JSON_SCHEMA = """{{
  "title": "string (5-200 chars) - REQUIRED",
  "summary": "string (20-1000 chars) - REQUIRED",
  "destination": "string - REQUIRED",
  "total_budget_estimate": number - REQUIRED,
  "currency": "{currency}" - REQUIRED,
  "duration_days": number (1-15) - REQUIRED,
  "itinerary": [
    {{
      "day_index": number (1-indexed) - REQUIRED,
      "order_index": number (1-indexed within day) - REQUIRED,
      "title": "string" - REQUIRED,
      "description": "string (10-1000 chars)" - REQUIRED,
      "place_name": "string" - REQUIRED,
      "coordinates": {{"lat": number, "lng": number}} - REQUIRED (use real coordinates),
      "estimated_cost": number - REQUIRED (estimate if unknown),
      "duration_minutes": number (15-480) - REQUIRED,
      "start_time": "HH:MM" - REQUIRED,
      "category": "food" | "culture" | "nature" | "history" | "shopping" | "nightlife" - REQUIRED,
      "rationale": "string (10-500 chars)" - REQUIRED
    }}
  ],
  "tags": ["string"] - REQUIRED (at least 3 tags),
  "tips": ["string"] - REQUIRED (at least 2 tips)
}}"""

EXPLAIN_SYSTEM_PROMPT_JSON_SCHEMA = """{
  "explanation": "string - detailed text explanation of the itinerary (REQUIRED)",
  "highlights": ["string"] - list of 3-5 key highlights (REQUIRED),
  "answered_question": "string or null - answer to specific question if provided"
}"""

IMPROVE_SYSTEM_PROMPT_JSON_SCHEMA = """{
  "improved_plan": <full TripPlan object with all fields>,
  "changes_made": ["string"] - list of specific changes made (REQUIRED),
  "improvement_summary": "string - brief summary of improvements (REQUIRED)"
}"""
  

RECOMMENDATION_SYSTEM_PROMPT = """You are an experienced travel planner and local guide.
Your task is to create a detailed, personalized travel itinerary.

CRITICAL RULES:
1. You MUST use ONLY places from the PROVIDED "AVAILABLE PLACES" list below
2. Copy coordinates (lat, lng) EXACTLY from the provided POI data - DO NOT invent coordinates
3. Use the price_uah from POI data as estimated_cost
4. Fill ALL fields - NO null values allowed
5. Respond ONLY with valid JSON, no additional text
6. Use {language} language for all descriptions and content
7. Consider weather when choosing activities (museums in rain, parks in sunshine)
8. Optimize logistics - group nearby locations together
9. Add rationale (explanation) for each activity choice
10. All costs must be in {currency}
11. Time format: HH:MM (plan realistic times: breakfast 09:00, lunch 13:00, dinner 19:00)
12. Duration: 60-180 minutes per activity

REQUIRED JSON SCHEMA:
{json_schema}
"""

# User prompt template for itinerary generation
RECOMMENDATION_USER_PROMPT = """Create a travel itinerary with the following parameters:

USER PROFILE:
- Interests: {interests}
- Transport: {transport_modes}
- Daily budget: {daily_budget} {currency}

TRIP CONSTRAINTS:
- Origin city: {origin_city}
- Destination city: {destination_city}
- Duration: {duration_days} days
- Total budget: {total_budget} {currency}
- Number of travelers: {party_size}
{weather_context}
{pois_context}

IMPORTANT: 
- Select places ONLY from the AVAILABLE PLACES list above
- Copy the exact lat/lng coordinates from each POI
- Use price_uah as estimated_cost
- Plan 3-5 activities per day with realistic timing

Create a detailed itinerary in JSON format. Respond in {language} language."""

# System prompt for explanation
EXPLAIN_SYSTEM_PROMPT = """You are a travel expert explaining itinerary choices.
Respond ONLY with valid JSON in {language} language.

REQUIRED JSON SCHEMA:
{json_schema}

IMPORTANT: "explanation" must be a single string with detailed text, NOT an object.
"""

# User prompt template for explanation
EXPLAIN_USER_PROMPT = """Explain this travel itinerary:

{trip_plan}

{question_context}

Respond with a JSON object containing:
- "explanation": a detailed TEXT string explaining the itinerary
- "highlights": array of 3-5 key highlights as strings
- "answered_question": answer to the question if provided, or null

Respond in {language} language."""

# System prompt for improvement
IMPROVE_SYSTEM_PROMPT = """You are a travel expert improving itineraries.
Respond ONLY with valid JSON in {language} language.
All costs in {currency}.
"""

# User prompt template for improvement
IMPROVE_USER_PROMPT = """Improve this itinerary:

CURRENT ITINERARY:
{current_plan}

IMPROVEMENT REQUEST:
{improvement_request}
{constraints_context}

Respond in JSON format with the complete updated itinerary in {language} language.
All costs in {currency}."""

ERROR_SYSTEM_PROMPT = """Your previous response had validation errors:

ERROR: {error}

INVALID RESPONSE:
{invalid_response}

Please fix the errors and return a valid JSON response that matches the required schema.
All required fields must be present and have correct types."""
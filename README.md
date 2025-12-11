# AI Recommender Service

AI-powered travel itinerary recommender service for LittleLifeTrip.

## Features

- Generate personalized travel itineraries using LLM (OpenAI, Gemini, Anthropic)
- Explain generated plans
- Improve existing itineraries based on user feedback
- JWT authentication for service-to-service communication
- Async PostgreSQL with SQLAlchemy
- Telemetry & Logging of all AI interactions

## Quick Start

### Local Development

1. **Clone and navigate**
   ```bash
   cd llt-ai-recomender
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and DB credentials
   ```

5. **Start Database (Docker)**
   ```bash
   docker-compose up -d db
   ```

6. **Run Migrations**
   ```bash
   alembic upgrade head
   ```

7. **Run the Server**
   ```bash
   uvicorn app.main:app --reload
   ```

### Docker Full Setup

```bash
docker-compose up -d --build
docker-compose exec llt-ai-recomender alembic upgrade head
```

## API Documentation

Swagger UI available at: `http://localhost:8000/docs`

### Key Endpoints

#### `POST /internal/v1/ai/recommend`
Generate new itinerary.
```json
{
  "user_id": "uuid",
  "user_profile": { "interests": ["food"], "transport_modes": ["walking"] },
  "constraints": { "origin_city": "Kyiv", "duration_days": 2 }
}
```

#### `POST /internal/v1/ai/explain`
Explain details of a trip.
```json
{
  "user_id": "uuid",
  "trip_id": "uuid",
  "trip_plan": { ... },
  "question": "Why this hotel?"
}
```

#### `POST /internal/v1/ai/improve`
Modify existing itinerary.
```json
{
  "user_id": "uuid",
  "trip_id": "uuid",
  "current_plan": { ... },
  "improvement_request": "Add more museums"
}
```

## Project Structure

```
llt-ai-recomender/
├── app/
│   ├── main.py              # Application entry point
│   ├── api/                 # API Routes & Dependencies
│   ├── core/                # Config, DB, Constants
│   ├── models/              # SQLAlchemy Database Models
│   ├── schemas/             # Pydantic Data Schemas
│   └── services/            # Business Logic (LLM, Telemetry, Recommendation)
├── alembic/                 # Migrations
├── requirements.txt         # Dependencies
├── compose.yml              # Docker Compose
└── llt-ai-recomender.postman_collection.json
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | Postgres connection string | required |
| `JWT_SECRET_KEY` | Secret for verifying tokens | required |
| `OPENAI_API_KEY` | Key for OpenAI | optional |
| `GEMINI_API_KEY` | Key for Google Gemini | optional |
| `ANTHROPIC_API_KEY` | Key for Anthropic Claude | optional |
| `DEFAULT_LLM_PROVIDER`| openai / gemini / anthropic | openai |
| `DEBUG` | Enable debug mode | False |

# AI Recommender Service

AI-powered travel itinerary recommender service for LittleLifeTrip.

## Features

- Generate personalized travel itineraries using LLM (OpenAI, Gemini, Anthropic)
- Explain generated plans
- Improve existing itineraries based on user feedback
- JWT authentication for service-to-service communication
- Async PostgreSQL with SQLAlchemy

## Quick Start

### Local Development

```bash
# 1. Clone and navigate
cd llt-ai-recomender

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env with your API keys

# 5. Run the server
uvicorn app.main:app --reload
```

### Docker

```bash
# Start with Docker Compose
docker-compose up -d

# Run migrations
docker-compose exec llt-ai-recomender alembic upgrade head
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/internal/v1/ai/recommend` | POST | Generate itinerary |
| `/internal/v1/ai/explain` | POST | Explain itinerary |
| `/internal/v1/ai/improve` | POST | Improve itinerary |

## Project Structure

```
llt-ai-recomender/
├── app/
│   ├── main.py              # FastAPI application
│   ├── core/                # Configuration & database
│   ├── models/              # SQLAlchemy models
│   ├── schemas/             # Pydantic schemas
│   ├── services/            # Business logic
│   └── api/                 # API routes
├── alembic/                 # Database migrations
├── requirements.txt
├── Dockerfile
└── docker-compose.yml
```

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `DATABASE_URL` | PostgreSQL connection string | Yes |
| `OPENAI_API_KEY` | OpenAI API key | At least one LLM key |
| `GEMINI_API_KEY` | Google Gemini API key | At least one LLM key |
| `ANTHROPIC_API_KEY` | Anthropic API key | At least one LLM key |
| `JWT_SECRET_KEY` | Secret key for JWT | Yes |
| `DEFAULT_LLM_PROVIDER` | Default provider (openai/gemini/anthropic) | No (default: openai) |


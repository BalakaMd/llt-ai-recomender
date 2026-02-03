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
│   │   ├── routes.py        # FastAPI route definitions
│   │   └── deps.py          # Dependency injection
│   ├── core/                # Config, DB, Constants
│   │   ├── config.py        # Application settings
│   │   ├── database.py      # Database connection
│   │   └── constants.py     # LLM providers, enums
│   ├── models/              # SQLAlchemy Database Models
│   │   └── ai_runs.py       # AI run telemetry model
│   ├── schemas/             # Pydantic Data Schemas
│   │   ├── request.py       # Request models
│   │   └── response.py      # Response models
│   └── services/            # Business Logic
│       ├── recommendation.py # Main recommendation service
│       ├── llm_engine.py    # LLM abstraction layer
│       ├── integration_client.py # External API client
│       ├── telemetry.py     # Telemetry & logging
│       └── prompts.py       # Prompt templates
├── tests/                   # Test suite
│   ├── conftest.py          # Pytest configuration & fixtures
│   ├── test_schemas_request.py # Request schema tests
│   ├── test_schemas_response.py # Response schema tests
│   └── test_recommendation_service.py # Service layer tests
├── alembic/                 # Database migrations
├── requirements.txt         # Python dependencies
├── pytest.ini             # Pytest configuration
├── docker-compose.yml      # Docker setup
└── README.md               # This file
```

## Testing

The project includes a comprehensive test suite covering all major components.

### Running Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_schemas_request.py

# Run with coverage (requires pytest-cov)
pytest --cov=app tests/
```

### Test Coverage

The test suite covers:

- **Schema Validation** (`test_schemas_request.py`, `test_schemas_response.py`)
  - Pydantic model validation
  - Field constraints and edge cases
  - Default values and optional fields

- **Business Logic** (`test_recommendation_service.py`)
  - Recommendation generation workflow
  - Error handling and failure scenarios
  - Integration with external services (mocked)

- **Async Support**
  - All async functions properly tested with pytest-asyncio
  - Background task verification

### Test Structure

- **Fixtures**: Shared test data in `conftest.py`
- **Mocks**: External dependencies mocked for isolated testing
- **Validation**: Comprehensive coverage of validation rules

### Test Statistics

```bash
pytest --tb=short
# Expected: 56 tests passing
```

## Development

### Code Quality

```bash
# Install development dependencies
pip install pytest pytest-asyncio pytest-cov black flake8

# Run linting
flake8 app/

# Format code
black app/ tests/

# Type checking (optional)
pip install mypy
mypy app/
```

### Adding New Tests

1. Create test functions following naming convention `test_*`
2. Use existing fixtures from `conftest.py` when possible
3. Mock external dependencies using `unittest.mock`
4. Test both success and failure scenarios
5. Add validation tests for new schema fields

### Database Testing

For database-related tests, use the test database configuration:

```bash
# Set test database URL
export DATABASE_URL="postgresql+asyncpg://test_user:test_pass@localhost:5432/test_db"

# Run migrations for test database
alembic upgrade head
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

## Architecture Overview

The service follows a clean architecture pattern with clear separation of concerns:

### Core Components

1. **API Layer** (`app/api/`)
   - FastAPI routes with JWT authentication
   - Request/response validation using Pydantic

2. **Business Logic** (`app/services/`)
   - `RecommendationService`: Main orchestration logic
   - `LLMEngine`: Abstraction over multiple LLM providers
   - `IntegrationClient`: External API communications
   - `TelemetryService`: Audit logging and metrics

3. **Data Layer** (`app/models/`, `app/schemas/`)
   - SQLAlchemy models for database persistence
   - Pydantic schemas for API contracts

### Workflow

1. **Recommendation Request**:
   - Validate request schemas
   - Fetch external data (weather, POIs)
   - Generate prompts and call LLM
   - Log interaction and return response

2. **Async Processing**:
   - Background tasks for telemetry logging
   - Non-blocking external API calls
   - Proper error handling and rollback

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass (`pytest`)
5. Submit a pull request

## License

[Add your license information here]

---

**LittleLifeTrip AI Recommender Service**  
Powered by modern LLM providers and FastAPI

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings

# Create FastAPI application
app = FastAPI(
    title="AI Recommender Service",
    description="AI-powered travel itinerary recommender service for LittleLifeTrip",
    version="0.1.0",
    docs_url="/recommender/docs" if settings.DEBUG else None,
    redoc_url="/recommender/redoc" if settings.DEBUG else None,
)

# CORS middleware (for internal service communication)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


from app.api.routes import router as api_router

# Include API router
app.include_router(api_router)


@app.get("/recommender/health", tags=["Health"])
async def health_check():
    """Health check endpoint for service monitoring."""
    return {"status": "ok", "service": "ai-recommender-service"}


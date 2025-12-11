from typing import AsyncGenerator, Annotated

from fastapi import Depends, HTTPException, status, Header
from sqlalchemy.ext.asyncio import AsyncSession
from jose import jwt, JWTError

from app.core.database import AsyncSessionLocal
from app.core.config import settings
from app.services import RecommendationService
from app.services.telemetry import TelemetryService
from app.services.integration_client import MockIntegrationClient
from app.services.llm_engine import LLMEngine


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Database session dependency."""
    async with AsyncSessionLocal() as session:
        yield session


async def verify_token(authorization: Annotated[str | None, Header()] = None) -> str:
    """
    Verify JWT token from Authorization header.
    Returns user_id or service_id from token.
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization header",
        )

    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication scheme",
            )

        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )

        # TODO: Extract user_id or service client_id from token
        # In a real scenario, we might extract user_id or service client_id
        # For now, we assume the token is valid if signature matches
        return payload.get("sub", "unknown_service")

    except (ValueError, JWTError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )


def get_telemetry_service(db: AsyncSession = Depends(get_db)) -> TelemetryService:
    """Telemetry service dependency."""
    return TelemetryService(db)


def get_integration_client() -> MockIntegrationClient:
    """Integration client dependency."""
    return MockIntegrationClient()


def get_llm_engine() -> LLMEngine:
    """LLM engine dependency."""
    return LLMEngine()


def get_recommendation_service(
    telemetry: TelemetryService = Depends(get_telemetry_service),
    integration: MockIntegrationClient = Depends(get_integration_client),
    llm: LLMEngine = Depends(get_llm_engine),
) -> RecommendationService:
    """Recommendation service dependency."""
    return RecommendationService(telemetry, integration, llm)

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ai_runs import AIRun
from app.core.constants import LLMProvider


class TelemetryService:
    """Service for managing AI run telemetry/logging."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_run(
        self,
        user_id: str,
        provider: LLMProvider,
        prompt: str,
        trip_id: Optional[str] = None,
    ) -> AIRun:
        """Create a new AI run record with pending status."""
        ai_run = AIRun(
            id=uuid.uuid4(),
            user_id=uuid.UUID(user_id),
            trip_id=uuid.UUID(trip_id) if trip_id else None,
            provider=provider.value,
            prompt=prompt,
            status='pending',
            created_at=datetime.utcnow(),
        )
        self.db.add(ai_run)
        await self.db.commit()
        await self.db.refresh(ai_run)
        return ai_run

    async def complete_run(
        self,
        run_id: uuid.UUID,
        response: dict,
        tokens_used: int,
    ) -> AIRun:
        """Mark AI run as completed with response data."""
        ai_run = await self.db.get(AIRun, run_id)
        if ai_run:
            ai_run.response = response
            ai_run.tokens_used = tokens_used
            ai_run.status = 'completed'  # Use string value for PostgreSQL ENUM
            ai_run.updated_at = datetime.utcnow()
            await self.db.commit()
            await self.db.refresh(ai_run)
        return ai_run

    async def fail_run(
        self,
        run_id: uuid.UUID,
        error_message: str,
    ) -> AIRun:
        """Mark AI run as failed with error message."""
        ai_run = await self.db.get(AIRun, run_id)
        if ai_run:
            ai_run.status = 'failed'  # Use string value for PostgreSQL ENUM
            ai_run.error_message = error_message
            ai_run.updated_at = datetime.utcnow()
            await self.db.commit()
            await self.db.refresh(ai_run)
        return ai_run

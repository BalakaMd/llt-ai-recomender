"""Initial migration - create integration schema and ai_runs table

Revision ID: 001_initial
Revises: 
Create Date: 2024-12-09

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001_initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create integration schema
    op.execute('CREATE SCHEMA IF NOT EXISTS integration')
    
    # Create LLMProvider enum
    llm_provider_enum = postgresql.ENUM('openai', 'gemini', 'anthropic', name='llmprovider', schema='integration')
    llm_provider_enum.create(op.get_bind(), checkfirst=True)
    
    # Create AIRunStatus enum
    ai_run_status_enum = postgresql.ENUM('pending', 'completed', 'failed', name='airunstatus', schema='integration')
    ai_run_status_enum.create(op.get_bind(), checkfirst=True)
    
    # Create ai_runs table
    op.create_table(
        'ai_runs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column('trip_id', postgresql.UUID(as_uuid=True), nullable=True, index=True),
        sa.Column('provider', postgresql.ENUM('openai', 'gemini', 'anthropic', name='llmprovider', schema='integration', create_type=False), nullable=False),
        sa.Column('prompt', sa.Text(), nullable=False),
        sa.Column('response', postgresql.JSONB(), nullable=True),
        sa.Column('tokens_used', sa.Integer(), nullable=True),
        sa.Column('status', postgresql.ENUM('pending', 'completed', 'failed', name='airunstatus', schema='integration', create_type=False), nullable=False, server_default='pending'),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=True, onupdate=sa.func.now()),
        schema='integration'
    )


def downgrade() -> None:
    # Drop table
    op.drop_table('ai_runs', schema='integration')
    
    # Drop enums
    op.execute('DROP TYPE IF EXISTS integration.airunstatus')
    op.execute('DROP TYPE IF EXISTS integration.llmprovider')
    
    # Drop schema (only if empty)
    op.execute('DROP SCHEMA IF EXISTS integration')

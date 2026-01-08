#!/bin/bash
set -e

echo "Starting AI Recommender Service..."

# Wait for database to be ready
echo "Waiting for database connection..."
while ! nc -z ${DB_HOST:-localhost} ${DB_PORT:-5432}; do
  echo "Database is unavailable - sleeping"
  sleep 1
done

echo "Database is ready - running migrations"

# Run database migrations
alembic upgrade head

echo "Migrations completed successfully"

# Start the application
echo "Starting FastAPI application..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000

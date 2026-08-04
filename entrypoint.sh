#!/bin/sh
set -e

echo "Waiting for database..."

until pg_isready -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER" -d "$POSTGRES_DB"; do
  echo "Database not ready, retrying in 2s..."
  sleep 2
done

echo "Database is ready. Running migrations..."

exec alembic upgrade head

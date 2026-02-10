#!/bin/bash

# Exit on error
set -e

if [ -n "$DB_HOST" ]; then
  echo "Waiting for PostgreSQL to be ready..."

  # Wait for database to be ready using pg_isready
  while ! pg_isready -h $DB_HOST -p $DB_PORT -U $DB_USER > /dev/null 2>&1; do
    echo "Waiting for postgresql at $DB_HOST:$DB_PORT..."
    sleep 1
  done

  echo "PostgreSQL is ready!"
else
  echo "DB_HOST is not set; skipping PostgreSQL readiness check."
fi

# Ensure static and media directories are writable
mkdir -p /app/staticfiles /app/media
chmod -R 775 /app/staticfiles /app/media

# Run migrations
echo "Running migrations..."
python manage.py migrate

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Starting Gunicorn..."
# Start Gunicorn
exec gunicorn playground.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers 4

#!/bin/bash

# Exit on error
set -e

# Ensure static and media directories exist
mkdir -p /app/staticfiles /app/media

# Run migrations
echo "Applying database migrations..."
python manage.py migrate --noinput

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Use PORT environment variable if set (Render provides this), otherwise default to 8000
PORT=${PORT:-8000}
echo "Starting Gunicorn on port $PORT..."
exec gunicorn playground.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --timeout 120

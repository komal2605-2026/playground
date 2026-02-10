#!/bin/bash

# Exit on error
set -e

echo "Waiting for PostgreSQL to be ready..."

# Extract database host and port from DATABASE_URL or use DB_HOST/DB_PORT env vars
if [ -n "$DATABASE_URL" ]; then
    # Parse DATABASE_URL to get host and port (format: postgresql://user:pass@host:port/dbname)
    DB_HOST_PARSED=$(echo $DATABASE_URL | sed -E 's#.*@([^:/]+).*#\1#')
    DB_PORT_PARSED=$(echo $DATABASE_URL | sed -E 's#.*:([0-9]+)/.*#\1#')
    
    # Wait for database using parsed values
    while ! pg_isready -h $DB_HOST_PARSED -p $DB_PORT_PARSED > /dev/null 2>&1; do
        echo "Waiting for postgresql at $DB_HOST_PARSED:$DB_PORT_PARSED..."
        sleep 1
    done
else
    # Use environment variables (Docker Compose setup)
    while ! pg_isready -h $DB_HOST -p $DB_PORT -U $DB_USER > /dev/null 2>&1; do
        echo "Waiting for postgresql at $DB_HOST:$DB_PORT..."
        sleep 1
    done
fi

echo "PostgreSQL is ready!"

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
# Use PORT environment variable if set (Render provides this), otherwise default to 8000
PORT=${PORT:-8000}
exec gunicorn playground.wsgi:application --bind 0.0.0.0:$PORT --workers 4

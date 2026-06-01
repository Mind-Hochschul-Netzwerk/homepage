#!/bin/bash
# This is called by the `web` service in `docker-compose.yml` when the container starts. 
set -e
echo "Running database migrations..."
uv run python manage.py migrate --noinput
echo "Starting application server..."
exec "$@"
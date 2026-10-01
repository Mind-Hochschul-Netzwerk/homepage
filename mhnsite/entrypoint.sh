#!/bin/bash
# This is called by the `app` service in `compose.yml` when the container starts.
# Runs as root so it can fix ownership of persistent bind mounts before
# dropping to the unprivileged "wagtail" user.
set -e
chown -R wagtail:wagtail /app/data /app/media
echo "Running database migrations..."
gosu wagtail uv run python manage.py migrate --noinput
echo "Starting application server..."
exec gosu wagtail "$@"
